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
import base64
import requests
import yaml
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPDigestAuth, HTTPBasicAuth, AuthBase
from requests.exceptions import RequestException
import httplib2
import oauth2client.client
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from PIL import Image, ImageEnhance
from twilio.rest import Client as TwilioRestClient
import pycountry
from jinja2.runtime import UndefinedError
from jinja2.exceptions import TemplateError
import dateutil
import dateutil.parser
import babel.dates
# import redis
import phonenumbers
from bs4 import BeautifulSoup
import i18naddress
from pyzbar.pyzbar import decode
from docxtpl import InlineImage, Subdoc, DocxTemplate
# import tablib
from docx import Document
from pikepdf import Pdf
import google.cloud
from docassemble.base.config import in_celery, daconfig
from docassemble.base.error import DAError, DAValidationError, DAIndexError, DAWebError, LazyNameError, DAAttributeError, DAException
from docassemble.base.file_docx import include_docx_template
from docassemble.base.filter import markdown_to_html
from docassemble.base.functions import alpha, roman, item_label, comma_and_list, get_language, set_language, get_dialect, get_voice, set_country, get_country, word, comma_list, ordinal, ordinal_number, need, nice_number, quantity_noun, possessify, verb_past, verb_present, noun_plural, noun_singular, space_to_underscore, force_ask, force_gather, period_list, name_suffix, currency_symbol, currency, indefinite_article, nodoublequote, capitalize, title_case, url_of, do_you, did_you, does_a_b, did_a_b, were_you, was_a_b, have_you, has_a_b, your, her, his, their, is_word, get_locale, set_locale, update_locale, process_action, url_action, get_info, set_info, get_config, prevent_going_back, qr_code, action_menu_item, from_b64_json, defined, define, value, message, response, json_response, command, single_paragraph, quote_paragraphs, location_returned, location_known, user_lat_lon, interview_url, interview_url_action, interview_url_as_qr, interview_url_action_as_qr, interview_email, get_emails, static_image, action_arguments, action_argument, language_functions, language_function_constructor, get_default_timezone, user_logged_in, interface, user_privileges, user_has_privilege, user_info, current_context, background_action, background_response, background_response_action, background_error_action, us, set_live_help_status, chat_partners_available, phone_number_in_e164, phone_number_formatted, phone_number_is_valid, countries_list, country_name, write_record, read_records, delete_record, variables_as_json, all_variables, server, language_from_browser, device, plain, bold, italic, states_list, state_name, subdivision_type, indent, raw, fix_punctuation, set_progress, get_progress, referring_url, undefine, invalidate, dispatch, yesno, noyes, split, showif, showifdef, phone_number_part, set_parts, log, encode_name, decode_name, interview_list, interview_menu, server_capabilities, session_tags, get_chat_log, get_user_list, get_user_info, set_user_info, get_user_secret, create_user, invite_user, create_session, get_session_variables, set_session_variables, get_question_data, go_back_in_session, manage_privileges, salutation, redact, ensure_definition, forget_result_of, re_run_logic, reconsider, set_title, set_save_status, single_to_double_newlines, CustomDataType, verbatim, add_separators, update_ordinal_numbers, update_ordinal_function, update_language_function, update_nice_numbers, update_word_collection, store_variables_snapshot, get_uid, update_terms, possessify_long, a_in_the_b, its, the, this, these, underscore_to_space, some, set_variables, language_name, run_action_in_session  # noqa: F401 # pylint: disable=unused-import
from docassemble.base.generate_key import random_alphanumeric, random_string
from docassemble.base.logger import logmessage
from docassemble.base.pandoc import word_to_markdown, concatenate_files, can_convert_word_to_markdown
import docassemble.base.file_docx
import docassemble.base.filter
import docassemble.base.functions
import docassemble.base.geocode
import docassemble.base.pandoc
import docassemble.base.parse
import docassemble.base.pdftk
from docassemble.base import DA
from docassemble.webapp.da_flask_mail import Message
import google_auth_httplib2

capitalize_func = capitalize
NoneType = type(None)

valid_variable_match = re.compile(r'^[^\d][A-Za-z0-9\_]*$')
match_inside_and_outside_brackets = re.compile(r'(.*)\[([^\]]+)\]$')
is_number = re.compile(r'^[0-9]+$')

DISABLED = 0
LOCAL = 1
REMOTE = 2
TESSERACT_PATH = 'tesseract'
if daconfig.get('tesseract with celery', False):
    TESSERACT_MODE = REMOTE
    from docassemble.tesseract.tasks import run_tesseract, run_gs  # pylint: disable=import-error,no-name-in-module,ungrouped-imports
elif TESSERACT_PATH and shutil.which(TESSERACT_PATH):
    TESSERACT_MODE = LOCAL
else:
    TESSERACT_MODE = DISABLED

QPDF_PATH = 'qpdf'
DEFAULT_BLUE_ICON = {'background': 'blue', 'borderColor': 'blue', 'glyph': None}

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
    'update_locale',
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
    'BackgroundAction',
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
    'current_context',
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
    'invite_user',
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
    if can_convert_word_to_markdown():
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
    """An object that silently absorbs any attribute access or operation.

    DAEmpty avoids triggering errors about missing information by returning
    another DAEmpty for any attribute access, returning empty values for
    string conversion and length, and absorbing arithmetic operations.

    Attributes:
        str (str): The string value returned when the object is converted to
            text. Defaults to the empty string.
    """

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

    def as_dict(self):
        return self.to_json()

    def to_json(self):
        output = {'_class': 'docassemble.base.util.DAEmpty'}
        try:
            output.update({'str': object.__getattribute__(self, 'str')})
        except Exception:
            pass
        return output


class DAObjectPlusParameters:
    """A wrapper pairing a DAObject with initialization parameters for lazy object construction."""
    pass


class DAObject:
    """Base class for all docassemble objects.

    DAObjects are special Python objects whose attributes can be defined
    interactively by docassemble interview questions. When code or a template
    refers to an undefined attribute of a DAObject, docassemble searches for
    a question or code block that can define it, rather than raising an
    AttributeError immediately.

    Every DAObject has an ``instanceName`` attribute that stores the variable
    name used when the object was created. This intrinsic name is used to
    find the appropriate question or code block when an attribute is undefined.

    Attributes:
        instanceName (str): The variable name of the object within the
            interview namespace (e.g., ``'client'`` or ``'client.address'``).
        has_nonrandom_instance_name (bool): True if the instance name was set
            explicitly; False if a random name was generated.
        attrList (list): A list of attribute names that have been set on this
            object.
    """

    def init(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        """Initialize the object by setting keyword arguments as attributes.

        This method is called by ``__init__`` after the instance name is
        established. Subclasses can override it to perform custom
        initialization while still calling ``super().init()``.

        Args:
            *pargs: Positional arguments (unused in base implementation).
            **kwargs: Each keyword argument is set as an attribute on the
                object.
        """
        for key, the_value in kwargs.items():
            setattr(self, key, the_value)

    @classmethod
    def using(cls, **kwargs):
        """Return a class-with-parameters object for use with DAList/DADict.

        This is used as an argument to ``object_type`` or
        ``appendObject()`` when you want the new objects to be initialized
        with specific keyword arguments.

        Args:
            **kwargs: Keyword arguments that will be passed to the ``init``
                method when new objects of this class are created.

        Returns:
            DAObjectPlusParameters: An object that bundles the class and the
                initialization parameters.
        """
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
        """Return the full variable name for an attribute.

        Useful when passing variable names (as strings) to functions like
        ``force_ask()`` and ``reconsider()``.

        Args:
            attr (str): The attribute name.

        Returns:
            str: The full dotted variable name, e.g. ``'person[3].birthdate'``.
        """
        return self.instanceName + '.' + attr

    def delattr(self, *pargs):
        """Delete one or more attributes, ignoring those that are not defined.

        Args:
            *pargs (str): Attribute names to delete.
        """
        for attr in pargs:
            if hasattr(self, attr):
                delattr(self, attr)

    def invalidate_attr(self, *pargs):
        """Invalidate one or more attributes, preserving their values as defaults.

        Like ``delattr()``, but the old value is remembered as the default
        when the interview asks the question again.

        Args:
            *pargs (str): Attribute names to invalidate.
        """
        for attr in pargs:
            if hasattr(self, attr):
                invalidate(self.instanceName + '.' + attr)

    def getattr_fresh(self, attr):
        """Recompute an attribute via reconsider() and return the fresh value.

        Should only be used on attributes that are defined by ``code`` blocks,
        not by questions posed to the user.

        Args:
            attr (str): The attribute name to recompute.

        Returns:
            The recomputed attribute value.
        """
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
        query_params.update({'involves': self, 'relationship_type': relationship_type})
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

    def get_point_of_view(self):
        if hasattr(self, '_point_of_view'):
            return self._point_of_view
        if self is docassemble.base.functions.this_thread.global_vars.user:
            return '2'
        return None

    def fix_instance_name(self, old_instance_name, new_instance_name):
        """Replace the instance name prefix for this object and all sub-objects.

        Args:
            old_instance_name (str): The old prefix to replace.
            new_instance_name (str): The new prefix to use.
        """
        self.instanceName = re.sub(r'^' + re.escape(old_instance_name), new_instance_name, self.instanceName)
        for aname in self.__dict__:
            if isinstance(getattr(self, aname), DAObject):
                getattr(self, aname).fix_instance_name(old_instance_name, new_instance_name)
        self.has_nonrandom_instance_name = True

    def set_instance_name(self, thename):
        """Set the instanceName, but only if it has not already been set explicitly.

        Args:
            thename (str): The desired instance name.
        """
        if not self.has_nonrandom_instance_name:
            self.instanceName = thename
            self.has_nonrandom_instance_name = True
        # else:
        #     logmessage("Not resetting name of " + self.instanceName)

    def set_random_instance_name(self):
        """Set the instanceName attribute to a randomly generated value."""
        self.instanceName = str(get_unique_name())
        self.has_nonrandom_instance_name = False

    def copy_shallow(self, thename):
        """Return a shallow copy of the object with a new instance name.

        Sub-objects are shared references; modifying them in the copy will
        also modify them in the original.

        Args:
            thename (str): The instance name to assign to the new object.

        Returns:
            DAObject: A shallow copy of this object.
        """
        new_object = copy.copy(self)
        new_object.instanceName = thename
        return new_object

    def copy_deep(self, thename):
        """Return a deep copy of the object with new instance names throughout.

        Sub-objects are fully copied and their instance names are updated to
        reflect their position within the new object hierarchy.

        Args:
            thename (str): The instance name to assign to the new object.

        Returns:
            DAObject: A deep copy of this object.
        """
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

    def raise_undefined_attribute_error(self, thename):
        """Raise a DAAttributeError for the named attribute, as if the attribute were undefined.

        Useful when implementing ``@property`` getter/setter pairs that need
        to trigger docassemble's question-seeking behavior.

        Args:
            thename (str): The attribute name that is considered undefined.

        Raises:
            DAAttributeError: Always raised.
        """
        var_name = object.__getattribute__(self, 'instanceName') + "." + thename
        docassemble.base.functions.this_thread.misc['pending_error'] = DAAttributeError("name '" + var_name + "' is not defined")
        raise docassemble.base.functions.this_thread.misc['pending_error']

    def object_name(self, **kwargs):
        """Return a human-readable name for the object based on its instance name.

        Converts dotted variable names into readable phrases. For example,
        ``case.plaintiff`` becomes ``"plaintiff in the case"``.

        Args:
            **kwargs: Accepts ``capitalize=True`` to capitalize the result.

        Returns:
            str: A human-readable name derived from the instance name.
        """
        the_name = reduce(a_in_the_b, map(object_name_convert, reversed(self.instanceName.split("."))))
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(the_name)
        return the_name

    def as_serializable(self):
        """Return a simplified, serializable representation of the object.

        Objects are converted to Python dicts so that the result can be
        serialized to JSON or other formats. The conversion is not reversible.

        Returns:
            dict: A serializable dict representation of the object.
        """
        return docassemble.base.functions.safe_json(self)

    def possessive(self, target, **kwargs):
        """Return a possessive phrase appropriate to this object.

        Args:
            target (str): The noun to be possessed, e.g. ``'fish'``.
            **kwargs: Optional keyword arguments including ``capitalize``
                (bool) and ``person`` (str, one of ``'1'``, ``'2'``,
                ``'3'``, ``'1p'``, ``'2p'``).

        Returns:
            str: E.g. ``"your fish"`` if the object is the user, or
            ``"John Smith's fish"`` otherwise.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            return your(target, **kwargs)
        if person == '2p':
            return docassemble.base.functions.your_plural(target, **kwargs)
        if person == '1':
            return docassemble.base.functions.my_possessive(target, **kwargs)
        if person == '1p':
            return docassemble.base.functions.our_possessive(target, **kwargs)
        return possessify(self, target, **kwargs)

    def object_possessive(self, target, **kwargs):
        """Return a possessive phrase based on the instance name rather than the object's value.

        Args:
            target (str): The noun to be possessed, e.g. ``'fish'``.
            **kwargs: Optional keyword arguments including ``capitalize``
                (bool) and ``language`` (str).

        Returns:
            str: E.g. ``"client's fish"`` or ``"the latch of the front gate
            in the park"``.
        """
        language = kwargs.get('language', None)
        if len(self.instanceName.split(".")) > 1:
            return possessify_long(self.object_name(), target, language=language)
        return possessify(the(self.object_name(), language=language), target, language=language, capitalize=kwargs.get('capitalize', False))

    def is_are_you(self, **kwargs):
        """Return "are you" if the object is the user, or "is <name>" otherwise.

        Args:
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"are you"`` or ``"is John Smith"``.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.are_you(**kwargs)
        if person == '2p':
            output = docassemble.base.functions.are_you_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.am_i(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.are_we(**kwargs)
        else:
            output = is_word(str(self), **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def yourself_or_name(self, **kwargs):
        """Return "yourself" if the object is the user, otherwise the object as a string.

        Args:
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: ``"yourself"`` when object is the user, or ``str(self)``
            otherwise.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.yourself(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.yourselves(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.myself(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.ourselves(**kwargs)
        else:
            output = str(self)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def itself(self, **kwargs):
        """Return an appropriate reflexive pronoun for this object.

        Args:
            **kwargs: Accepts ``person`` (str, one of ``'1'``, ``'2'``,
                ``'1p'``, ``'2p'``) to force a particular person.

        Returns:
            str: ``"yourself"``, ``"itself"``, ``"myself"``, etc.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            return docassemble.base.functions.yourself(**kwargs)
        if person == '2p':
            return docassemble.base.functions.yourselves(**kwargs)
        if person == '1':
            return docassemble.base.functions.myself(**kwargs)
        if person == '1p':
            return docassemble.base.functions.ourselves(**kwargs)
        return docassemble.base.functions.itself(**kwargs)

    def is_user(self):
        """Return True if this object is the current user, otherwise False."""
        return self is docassemble.base.functions.this_thread.global_vars.user

    def initializeAttribute(self, *pargs, **kwargs):
        """Define an attribute as a newly initialized DAObject, if not already defined.

        The attribute will be created with an ``instanceName`` derived from
        this object's own ``instanceName``. If the attribute is already
        defined, this method has no effect and returns the existing attribute.

        Args:
            *pargs: First positional argument is the attribute name (str);
                second is the object class (or result of ``cls.using()``).
            **kwargs: Additional keyword arguments passed to the new object's
                ``init`` method.

        Returns:
            DAObject: The newly created (or already existing) attribute object.
        """
        pargs = list(pargs)
        if len(pargs) < 2:
            raise DAError("initializeAttribute requires an attribute name and an object type")
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
        """Redefine an attribute as a newly initialized DAObject, overwriting any existing value.

        Like ``initializeAttribute()``, but overwrites the attribute even if
        it is already defined.

        Args:
            *pargs: First positional argument is the attribute name (str);
                second is the object class (or result of ``cls.using()``).
            **kwargs: Additional keyword arguments passed to the new object's
                ``init`` method.

        Returns:
            DAObject: The newly created attribute object.
        """
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
        """Return True if the named attribute is defined, otherwise False.

        Unlike accessing the attribute directly, this method does not trigger
        the question-seeking process.

        Args:
            name (str): The attribute name to check.

        Returns:
            bool: True if the attribute is defined.
        """
        return hasattr(self, name)

    def attr(self, name):
        """Return the value of the named attribute, or None if it is not defined.

        Unlike ``getattr()``, this method does not trigger the question-seeking
        process when the attribute is not defined.

        Args:
            name (str): The attribute name.

        Returns:
            The attribute value, or None if not defined.
        """
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
        """Return a possessive pronoun phrase appropriate for this object.

        Args:
            target (str): The noun to be possessed, e.g. ``'reason'``.
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"its reason"``, ``"your reason"``, or ``"my reason"``.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = your(target, **kwargs)
        elif person == '2p':
            output = docassemble.base.functions.your_plural(target, **kwargs)
        elif person == '1':
            output = docassemble.base.functions.my_possessive(target, **kwargs)
        elif person == '1p':
            output = docassemble.base.functions.our_possessive(target, **kwargs)
        else:
            output = its(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun(self, **kwargs):
        """Return an objective pronoun appropriate for this object.

        For a generic DAObject (not an Individual), this returns ``"it"``
        for the third person. Subclasses like Individual override this.

        Args:
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"it"``, ``"you"``, or ``"me"``.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.you_objective(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.you_objective_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.me_objective(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.us_objective(**kwargs)
        else:
            output = docassemble.base.functions.it_objective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun_objective(self, **kwargs):
        """Return an objective pronoun. Identical to ``pronoun()`` for DAObject.

        Args:
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"it"`` or ``"you"``.
        """
        return self.pronoun(**kwargs)

    def pronoun_subjective(self, **kwargs):
        """Return a subjective pronoun appropriate for this object.

        For a generic DAObject (not an Individual), this returns ``"it"``
        for the third person.

        Args:
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"it"``, ``"you"``, or ``"I"``.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.you_subjective(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.you_subjective_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.i_subjective(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.we_subjective(**kwargs)
        else:
            output = docassemble.base.functions.it_subjective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def alternative(self, *pargs, **kwargs):
        """Return a value that depends on the current value of a named attribute.

        Args:
            *pargs: First positional argument is the attribute name (str).
            **kwargs: Keys are possible attribute values; the corresponding
                value is returned when the attribute matches. Use ``_default``
                or ``default`` as a fallback key.

        Returns:
            The value associated with the current attribute value, or None
            if no match and no default.
        """
        if len(pargs) == 0:
            raise DAError("alternative: attribute must be provided")
        attribute = pargs[0]
        the_value = getattr(self, attribute)
        if the_value in kwargs:
            return kwargs[the_value]
        if '_default' in kwargs:
            return kwargs['_default']
        if 'default' in kwargs:
            return kwargs['default']
        return None

    def do_question(self, the_verb, **kwargs):
        """Return a present-tense do-question appropriate for this object.

        Args:
            the_verb (str): The infinitive verb, e.g. ``'eat'``.
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"do you eat"`` or ``"does John Smith eat"``.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            return do_you(the_verb, **kwargs)
        if person == '2p':
            return docassemble.base.functions.do_you_plural(the_verb, **kwargs)
        if person == '1':
            return docassemble.base.functions.do_i(the_verb, **kwargs)
        if person == '1p':
            return docassemble.base.functions.do_we(the_verb, **kwargs)
        return does_a_b(self, the_verb, **kwargs)

    def did_question(self, the_verb, **kwargs):
        """Return a past-tense did-question appropriate for this object.

        Args:
            the_verb (str): The infinitive verb, e.g. ``'eat'``.
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"did you eat"`` or ``"did John Smith eat"``.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            return did_you(the_verb, **kwargs)
        if person == '2p':
            return docassemble.base.functions.did_you_plural(the_verb, **kwargs)
        if person == '1':
            return docassemble.base.functions.did_i(the_verb, **kwargs)
        if person == '1p':
            return docassemble.base.functions.did_we(the_verb, **kwargs)
        return did_a_b(self, the_verb, **kwargs)

    def were_question(self, the_target, **kwargs):
        """Return a past-tense were/was question appropriate for this object.

        Args:
            the_target (str): The predicate, e.g. ``'married'``.
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"were you married"`` or ``"was John Smith married"``.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            return were_you(the_target, **kwargs)
        if person == '2p':
            return docassemble.base.functions.were_you_plural(the_target, **kwargs)
        if person == '1':
            return docassemble.base.functions.was_i(the_target, **kwargs)
        if person == '1p':
            return docassemble.base.functions.were_we(the_target, **kwargs)
        return was_a_b(self, the_target, **kwargs)

    def have_question(self, the_target, **kwargs):
        """Return a present-perfect have/has question appropriate for this object.

        Args:
            the_target (str): The predicate, e.g. ``'signed'``.
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"have you signed"`` or ``"has John Smith signed"``.
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            return have_you(the_target, **kwargs)
        if person == '2p':
            return docassemble.base.functions.have_you_plural(the_target, **kwargs)
        if person == '1':
            return docassemble.base.functions.have_i(the_target, **kwargs)
        if person == '1p':
            return docassemble.base.functions.have_we(the_target, **kwargs)
        return has_a_b(self, the_target, **kwargs)

    def does_verb(self, the_verb, **kwargs):
        """Return the correctly conjugated present-tense form of a verb.

        Args:
            the_verb (str): The infinitive verb, e.g. ``'eat'``.
            **kwargs: Accepts ``capitalize`` (bool), ``person`` (str), and
                ``past`` (bool) to use past tense instead.

        Returns:
            str: E.g. ``"eat"`` (second person) or ``"eats"`` (third person).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            tense = '2sg'
        elif person == '2p':
            tense = '2pl'
        elif person == '1':
            tense = '1sg'
        elif person == '1p':
            tense = '1pl'
        else:
            tense = '3sg'
        if ('past' in kwargs and kwargs['past'] is True) or ('present' in kwargs and kwargs['present'] is False):
            return verb_past(the_verb, tense, **kwargs)
        return verb_present(the_verb, tense, **kwargs)

    def did_verb(self, the_verb, **kwargs):
        """Return the correctly conjugated past-tense form of a verb.

        Args:
            the_verb (str): The infinitive verb, e.g. ``'eat'``.
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"ate"`` or ``"ate"`` (conjugated for person).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            tense = '2sgp'
        elif person == '2p':
            tense = '2ppl'
        elif person == '1':
            tense = '1sgp'
        elif person == '1p':
            tense = '1ppl'
        else:
            tense = '3sgp'
        return verb_past(the_verb, tense, **kwargs)

    def subjective_pronoun_or_name(self, **kwargs):
        """Return a subjective pronoun if the object is the user, or the object as a string.

        Args:
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"you"`` (second person) or ``"John Smith"``
            (third person).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.you_subjective(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.you_subjective_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.i_subjective(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.we_subjective(**kwargs)
        else:
            output = str(self)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def pronoun_or_name(self, **kwargs):
        """Return an objective pronoun if the object is the user, or the object as a string.

        Args:
            **kwargs: Accepts ``capitalize`` (bool) and ``person`` (str).

        Returns:
            str: E.g. ``"you"`` (second person) or ``"John Smith"``
            (third person).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.you_objective(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.you_objective_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.me_objective(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.us_objective(**kwargs)
        else:
            output = str(self)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

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
    """A data structure that maps directed and peer relationships among objects.

    Maintains two collections: ``relationships_dir`` for directed parent/child
    relationships and ``relationships_peer`` for undirected peer relationships.
    Supports filtering queries via keyword arguments or filter functions.

    Attributes:
        leaf (DAList): Collection of all nodes (people or objects) tracked by
            this tree.
        relationships_dir (DAList): Collection of directed
            ``RelationshipDir`` objects.
        relationships_peer (DAList): Collection of undirected
            ``RelationshipPeer`` objects.
    """

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
        """Query peer relationships using a filter function or keyword match.

        Args:
            *pargs: Optional single filter function accepting a
                ``RelationshipPeer`` and returning bool.
            **kwargs: A single keyword argument used to build a filter
                automatically (e.g. ``involves=person``).

        Returns:
            generator: A generator of ``RelationshipPeer`` objects that match
                the filter.

        Raises:
            DAError: If the query arguments cannot be resolved to a valid
                filter function.
        """
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
        """Query directed relationships using a filter function or keyword match.

        Args:
            *pargs: Optional single filter function accepting a
                ``RelationshipDir`` and returning bool.
            **kwargs: A single keyword argument used to build a filter
                automatically (e.g. ``parent=person``).

        Returns:
            generator: A generator of ``RelationshipDir`` objects that match
                the filter.

        Raises:
            DAError: If the query arguments cannot be resolved to a valid
                filter function.
        """
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
        """Add or retrieve a directed (parent/child) relationship.

        Args:
            parent: The parent node of the relationship.
            child: The child node of the relationship.
            relationship_type: An identifier for the type of relationship.

        Returns:
            RelationshipDir: The existing or newly created relationship object.
        """
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
        """Delete one or more directed relationships from the tree.

        Args:
            *pargs: The ``RelationshipDir`` objects to remove.
        """
        self.relationships_dir.remove(*pargs)

    def add_relationship_peer(self, *pargs, **kwargs):
        """Add or retrieve an undirected (peer) relationship among nodes.

        Args:
            *pargs: The nodes that are peers in this relationship.
            relationship_type: Keyword argument identifying the type of
                relationship.

        Returns:
            RelationshipPeer: The existing or newly created peer relationship.
        """
        relationship_type = kwargs.get('relationship_type', None)
        the_set = set(pargs)
        for item in self.relationships_peer:
            if item.relationship_type == relationship_type and item.peers == the_set:
                return item
        # logmessage("Setting relationship involving " + repr(the_set) + " and reltype " + relationship_type)
        return self.relationships_peer.appendObject(peers=the_set, relationship_type=relationship_type)

    def delete_peer(self, *pargs):
        """Delete one or more peer relationships from the tree.

        Args:
            *pargs: The ``RelationshipPeer`` objects to remove.
        """
        self.relationships_peer.remove(*pargs)


class DAList(DAObject):
    """A list that docassemble can populate through interview questions.

    DAList behaves like a Python list, but docassemble can ask questions to
    define items of the list. It supports an automatic gathering process
    controlled by attributes such as ``there_are_any`` and
    ``there_is_another``.

    Attributes:
        elements (list): The underlying Python list of items.
        gathered (bool): True when all items have been gathered.
        auto_gather (bool): If True (the default), the gathering process is
            triggered automatically. Set to False to control gathering
            manually.
        object_type: A DAObject subclass (or result of ``.using()``) used
            when creating new items via ``appendObject()``. Defaults to None.
        complete_attribute (str or None): An attribute that must be defined
            on each item before the item is considered complete during
            gathering.
        ask_number (bool): If True, docassemble will ask for the number of
            items before gathering them.
        minimum_number (int or None): Minimum number of items to gather.
        there_are_any (bool): Whether any items exist. Sought by the
            gathering process when the list is empty.
        there_is_another (bool): Whether there is another item to add. Sought
            repeatedly during gathering.
    """

    def init(self, *pargs, **kwargs):
        self.elements = []
        if 'auto_gather' not in kwargs:
            self.auto_gather = True
        if 'ask_number' not in kwargs:
            self.ask_number = False
        if 'minimum_number' not in kwargs:
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
            if kwargs['ask_object_type']:
                self.ask_object_type = True
                self.object_type = None
                self.object_type_parameters = {}
            else:
                self.ask_object_type = False
            del kwargs['ask_object_type']
        if not hasattr(self, 'ask_object_type'):
            self.ask_object_type = False
        super().init(*pargs, **kwargs)

    def initializeObject(self, *pargs, **kwargs):
        """Create a new object at a given index in the list.

        Args:
            *pargs: First positional argument must be a non-negative integer
                index. An optional second positional argument is the class
                (or ``.using()`` result) to use for the new object. Falls
                back to ``object_type``, then ``new_object_type`` (when
                ``ask_object_type`` is True), then ``DAObject``.
            **kwargs: Additional keyword arguments are passed to the new
                object's constructor.

        Returns:
            DAObject: The newly created object stored at ``self[index]``.

        Raises:
            DAError: If the first argument is not a non-negative integer.
        """
        objectFunction = None
        pargs = list(pargs)
        if len(pargs) == 0 or not isinstance(pargs[0], int) or pargs[0] < 0:
            raise DAError("initializeObject: first parameter must be an integer (0 or greater)")
        index = pargs.pop(0)
        if len(pargs) > 0:
            objectFunction = pargs.pop(0)
        new_obj_parameters = {}
        if isinstance(objectFunction, DAObjectPlusParameters):
            for key, val in objectFunction.parameters.items():
                new_obj_parameters[key] = val
            objectFunction = objectFunction.object_type
        if objectFunction is None:
            if self.ask_object_type:
                if isinstance(self.new_object_type, DAObjectPlusParameters):
                    objectFunction = self.new_object_type.object_type
                    new_obj_parameters = self.new_object_type.parameters
                elif isinstance(self.new_object_type, type):
                    objectFunction = self.new_object_type
                else:
                    raise DAError("new_object_type must be an object type")
            elif self.object_type is not None:
                objectFunction = self.object_type
                for key, val in self.object_type_parameters.items():
                    new_obj_parameters[key] = val
            else:
                objectFunction = DAObject
        for key, val in kwargs.items():
            new_obj_parameters[key] = val
        newobject = objectFunction(self.instanceName + '[' + repr(index) + ']', *pargs, **new_obj_parameters)
        for pre_index in range(len(self.elements), index):  # pylint: disable=unused-variable
            self.elements.append(None)
        self[index] = newobject
        self.there_are_any = True
        if objectFunction is None and self.ask_object_type and hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        return newobject

    def set_object_type(self, object_type):
        """Set the object type used when creating new list items.

        Args:
            object_type: A class or ``.using()`` result to use when
                ``appendObject()`` creates new items.
        """
        if isinstance(object_type, DAObjectPlusParameters):
            self.object_type = object_type.object_type
            self.object_type_parameters = object_type.parameters
        else:
            self.object_type = object_type
            self.object_type_parameters = {}

    def cancel_add_or_edit(self):
        unique_id = docassemble.base.functions.this_thread.current_info['user']['session_uid']
        if 'event_stack' in docassemble.base.functions.this_thread.internal and unique_id in docassemble.base.functions.this_thread.internal['event_stack']:
            new_stack = []
            for item in docassemble.base.functions.this_thread.internal['event_stack'][unique_id]:
                if 'arguments' in item:
                    if 'list' in item['arguments'] and item['arguments']['list'] == self.instanceName:
                        continue
                    if 'group' in item['arguments'] and item['arguments']['group'] == self.instanceName:
                        continue
                if 'action' in item and item['action'].startswith(self.instanceName + '['):
                    continue
                new_stack.append(item)
            docassemble.base.functions.this_thread.internal['event_stack'][unique_id] = new_stack
        if self.complete_elements().number() < self.number_gathered():
            self.pop()
        self.delattr('doing_gathered_and_complete', '_necessary_length', 'there_is_one_other')

    def gathered_and_complete(self):
        """Ensure every item in the list is complete and return True.

        Resets ``gathered`` so the gathering process re-checks completeness,
        then calls ``gather()`` (or reads ``gathered`` for manual gathering).

        Returns:
            bool: Always True once all items are complete.
        """
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
        """Return the variable name for a list item by its index.

        Args:
            item (int): The index of the item.

        Returns:
            str: Variable name such as ``'mylist[0]'``, suitable for use
                in ``force_ask()`` and similar functions.
        """
        return self.instanceName + '[' + repr(item) + ']'

    def delitem(self, *pargs):
        """Delete items by index.

        Args:
            *pargs (int): Zero or more index numbers of items to delete.
                Indices that exceed the list length are silently ignored.
        """
        for item in reversed([item for item in pargs if item < len(self.elements)]):
            self.elements.__delitem__(item)  # pylint: disable=unnecessary-dunder-call
        self._reset_instance_names()

    def copy(self):
        """Returns a copy of the list."""
        return self.elements.copy()

    def filter(self, *pargs, **kwargs):
        """Return a new DAList containing only items matching the given attribute values.

        Args:
            *pargs: Optional first argument sets the instance name of the
                returned list; defaults to this list's instance name.
            **kwargs: Attribute name/value pairs used to filter items.
                Items where ``getattr(item, key) != val`` are excluded.

        Returns:
            DAList: A gathered copy containing only matching items.
        """
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
        """Reset the gathered state so the collection will be re-gathered.

        Args:
            recursive (bool): If True, also reset gathering on nested DAList
                and DADict objects within the collection. Defaults to False.
            only_if_empty (bool): If True, only reset if the collection is
                empty. Defaults to False.
            mark_incomplete (bool): If True, delete the ``complete_attribute``
                on each item so items are treated as incomplete. Defaults to
                False.
        """
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
        """Return True if the gathering process has completed.

        Returns:
            bool: True if the list has been gathered; False otherwise.
        """
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
        """Return the item at the given index, or a blank DAEmpty if out of range.

        Args:
            index (int): Zero-based position of the item.

        Returns:
            object: The item at ``index``, or a ``DAEmpty`` instance.
        """
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
        """Sort the list in place, trigger gathering first, and return self.

        Args:
            **kwargs: Keyword arguments passed to Python's ``sorted()``
                (e.g., ``key``, ``reverse``).

        Returns:
            DAList: This list object, for chaining.
        """
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
        """Sort the list in place without triggering gathering, and return self.

        Args:
            **kwargs: Keyword arguments passed to Python's ``sorted()``
                (e.g., ``key``, ``reverse``).

        Returns:
            DAList: This list object, for chaining.
        """
        self.elements = sorted(self.elements, **kwargs)
        self._reset_instance_names()
        return self

    def appendObject(self, *pargs, **kwargs):
        """Create a new object and append it to the list.

        Args:
            *pargs: An optional first positional argument specifies the class
                (or ``.using()`` result) for the new object. Falls back to
                ``object_type``, then ``new_object_type`` (when
                ``ask_object_type`` is True), then ``DAObject``.
            **kwargs: Additional keyword arguments passed to the new object's
                constructor.

        Returns:
            DAObject: The newly created object appended to the list.
        """
        # logmessage("Called appendObject where len is " + str(len(self.elements)))
        objectFunction = None
        if len(pargs) > 0:
            pargs = list(pargs)
            objectFunction = pargs.pop(0)
        new_obj_parameters = {}
        if objectFunction is None:
            if self.ask_object_type:
                if isinstance(self.new_object_type, DAObjectPlusParameters):
                    objectFunction = self.new_object_type.object_type
                    new_obj_parameters = self.new_object_type.parameters
                elif isinstance(self.new_object_type, type):
                    objectFunction = self.new_object_type
                else:
                    raise DAError("new_object_type must be an object type")
            elif self.object_type is not None:
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
        if objectFunction is None and self.ask_object_type and hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        return newobject

    def append(self, *pargs, **kwargs):
        """Add one or more items to the end of the list.

        Args:
            *pargs: Items to append. DAObject items without a non-random
                instance name are renamed to match their position in this
                list.
            **kwargs: Pass ``set_instance_name=True`` to force renaming of
                DAObject items even if they already have a non-random name.
        """
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
        """Remove items from the list by value.

        Args:
            *pargs: Values to remove. Items not found in the list are
                silently ignored. Sets ``there_are_any`` to False if the
                list becomes empty.
        """
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

    def is_user(self):
        """Returns True if the list has one element and that element is the user, otherwise False."""
        if self.number() == 1:
            self._trigger_gather()
            return self.elements[0].is_user()
        return False

    def itself(self, **kwargs):
        """Returns "themselves" unless the list has only one element,
        in which case the method is called on the first element."""
        self._trigger_gather()
        if self.number() == 1:
            if isinstance(self.elements[0], DAObject):
                return self.elements[0].itself(**kwargs)
            return docassemble.base.functions.itself(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.yourselves(**kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.ourselves(**kwargs)
        return docassemble.base.functions.themselves(**kwargs)

    def do_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "do x eat" if there is
        more than one element. x is the string representation of the
        list. If there is only one element, the method is called on
        the first element of the list.

        """
        self._trigger_gather()
        if self.number() == 1:
            if isinstance(self.elements[0], DAObject):
                return self.elements[0].do_question(the_verb, **kwargs)
            return does_a_b(self.elements[0], the_verb, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.do_you_plural(the_verb, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.do_we(the_verb, **kwargs)
        return docassemble.base.functions.do_a_b(self, the_verb, **kwargs)

    def did_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "did x eat" if there is
        more than one element. x is the string representation of the
        list. If there is only one element, the method is called on
        the first element of the list.

        """
        self._trigger_gather()
        if self.number() == 1:
            if isinstance(self.elements[0], DAObject):
                return self.elements[0].did_question(the_verb, **kwargs)
            return did_a_b(self.elements[0], the_verb, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.did_you_plural(the_verb, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.did_we(the_verb, **kwargs)
        return docassemble.base.functions.did_a_b_plural(self, the_verb, **kwargs)

    def were_question(self, the_target, **kwargs):
        """Given a target like "married", returns "were x married" if
        there is more than one element in the list. x is the string
        representation of the list. If there is only one element, the
        method is called on the first element."""
        self._trigger_gather()
        if self.number() == 1:
            if isinstance(self.elements[0], DAObject):
                return self.elements[0].were_question(the_target, **kwargs)
            return was_a_b(self.elements[0], the_target, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.were_you_plural(the_target, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.were_we(the_target, **kwargs)
        return docassemble.base.functions.were_a_b_plural(self, the_target, **kwargs)

    def have_question(self, the_target, **kwargs):
        """Given a target like "married", returns "have x married" if
        there is more than one element in the list. x is the string
        representation of the list. If there is only one element, the
        method is called on the first element.

        """
        self._trigger_gather()
        if self.number() == 1:
            if isinstance(self.elements[0], DAObject):
                return self.elements[0].have_question(the_target, **kwargs)
            return has_a_b(self.elements[0], the_target, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.have_you_plural(the_target, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.have_we(the_target, **kwargs)
        return docassemble.base.functions.have_a_b(self, the_target, **kwargs)

    def does_verb(self, the_verb, **kwargs):
        """Return the correctly conjugated present-tense form of a verb for the list.

        Args:
            the_verb (str): The base form of the verb (e.g., ``"sue"``).
            **kwargs: Accepts ``person`` (str), ``language`` (str), ``past``
                (bool), and ``present`` (bool) for tense control.

        Returns:
            str: Conjugated verb, e.g. "sues" for one plaintiff or "sue" for
                multiple plaintiffs.
        """
        language = kwargs.get('language', None)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if ('past' in kwargs and kwargs['past'] is True) or ('present' in kwargs and kwargs['present'] is False):
            if self.number() > 1:
                if person in ('2', '2p'):
                    tense = '2ppl'
                elif person in ('1', '1p'):
                    tense = '1ppl'
                else:
                    tense = '3ppl'
            else:
                if person == '2':
                    tense = '2sgp'
                elif person == '2p':
                    tense = '2ppl'
                elif person == '1':
                    tense = '1sgp'
                elif person == '1p':
                    tense = '1ppl'
                else:
                    tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
        if self.number() > 1:
            if person in ('2', '2p'):
                tense = '2pl'
            elif person in ('1', '1p'):
                tense = '1pl'
            else:
                tense = '3pl'
        else:
            if person == '2':
                tense = '2sg'
            elif person == '2p':
                tense = '2pl'
            elif person == '1':
                tense = '1sg'
            elif person == '1p':
                tense = '1pl'
            else:
                tense = '3sg'
        return verb_present(the_verb, tense, language=language)

    def did_verb(self, the_verb, **kwargs):
        """Return the correctly conjugated past-tense form of a verb for the collection.

        Args:
            the_verb (str): The base form of the verb (e.g., ``"sue"``).
            **kwargs: Accepts ``person`` (str) and ``language`` (str).

        Returns:
            str: Past-tense conjugated verb, e.g. "sued".
        """
        language = kwargs.get('language', None)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if self.number() > 1:
            if person in ('2', '2p'):
                tense = '2ppl'
            elif person in ('1', '1p'):
                tense = '1ppl'
            else:
                tense = '3ppl'
        else:
            if person == '2':
                tense = '2sgp'
            elif person == '2p':
                tense = '2ppl'
            elif person == '1':
                tense = '1sgp'
            elif person == '1p':
                tense = '1ppl'
            else:
                tense = '3sgp'
        return verb_past(the_verb, tense, language=language)

    def as_singular_noun(self):
        """Return the singular noun form derived from the list's instance name.

        E.g., ``case.plaintiff.child.as_singular_noun()`` returns ``"child"``
        regardless of how many children are in the list.

        Returns:
            str: Singular noun form of the trailing part of the instance name.
        """
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return noun_singular(the_noun)

    def possessive(self, target, **kwargs):
        """Return a possessive phrase using the list's noun form and the target.

        Args:
            target (str): The possessed noun phrase (e.g., ``"fish"``).
            **kwargs: Passed to ``possessify()``; may include ``language``.

        Returns:
            str: E.g., "plaintiff's fish" (one item) or "plaintiffs' fish"
                (multiple items).
        """
        language = kwargs.get('language', None)
        return possessify(self.as_noun(**kwargs), target, plural=(self.number() > 1), language=language)

    def is_are_you(self, **kwargs):
        """Returns "are" followed by the list object reduced to text,
        but if the list has only one element, the method is called on
        that element instead.
        """
        if self.number() == 1:
            self._trigger_gather()
            return self.elements[0].is_are_you(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            output = docassemble.base.functions.are_you_plural(**kwargs)
        elif person in ('1', '1p'):
            output = docassemble.base.functions.are_we(**kwargs)
        else:
            output = docassemble.base.functions.are_word(str(self), **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def quantity_noun(self, *pargs, **kwargs):
        """Returns the output of the quantity_noun() function using the number
        of elements in the list as the quantity."""
        the_args = [self.number()] + list(pargs)
        return quantity_noun(*the_args, **kwargs)

    def as_noun(self, *pargs, **kwargs):
        """Return a singular or plural noun form for the list, derived from the instance name.

        Uses singular when the list has exactly one element, plural otherwise.
        E.g., ``case.plaintiff.child.as_noun()`` returns ``"child"`` or
        ``"children"`` as appropriate.

        Args:
            *pargs: If provided, the first argument overrides the noun (instead
                of using the instance name).
            **kwargs: Accepts ``plural`` (bool), ``singular`` (bool),
                ``article`` (bool), ``some`` (bool), ``this`` (bool),
                ``capitalize`` (bool), and ``language`` (str).

        Returns:
            str: Noun form with optional article.
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
            return capitalize_func(output)
        return output

    def number(self):
        """Return the number of elements in the list, triggering gathering if needed.

        Returns:
            int: Count of items in the list.
        """
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return len(self.elements)

    def gathering_started(self):
        """Return True if any items have been gathered or ``there_are_any`` has been set.

        Returns:
            bool: True if gathering has started; False otherwise.
        """
        if hasattr(self, 'gathered') or hasattr(self, 'there_are_any') or len(self.elements) > 0:
            return True
        return False

    def number_gathered(self, if_started=False):
        """Return the count of items gathered so far, without triggering gathering.

        Args:
            if_started (bool): If True, trigger gathering when gathering has
                not yet started. Defaults to False.

        Returns:
            int: Number of items currently in the collection.
        """
        if if_started and not self.gathering_started():
            self._trigger_gather()
        return len(self.elements)

    def current_index(self):
        """Return the index of the last item added, or 0 if the list is empty.

        Returns:
            int: Zero-based index of the last element, or 0 when empty.
        """
        if len(self.elements) == 0:
            return 0
        return len(self.elements) - 1

    def number_as_word(self, language=None, capitalize=False):  # pylint: disable=redefined-outer-name
        """Return the number of items spelled out as a word when ten or fewer.

        Args:
            language (str, optional): Language code for localization.
            capitalize (bool): If True, capitalize the result. Defaults to
                False.

        Returns:
            str: Spelled-out number (e.g., "three") for counts up to ten;
                numeral string otherwise.
        """
        return nice_number(self.number(), language=language, capitalize=capitalize)

    def complete_elements(self, complete_attribute=None):
        """Return a gathered DAList of only the complete items.

        An item is complete if ``str()`` succeeds on it and, when
        ``complete_attribute`` is set, each attribute named therein is
        defined.

        Args:
            complete_attribute (str or list, optional): Override the list's
                own ``complete_attribute`` setting.

        Returns:
            DAList: A new DAList with ``gathered=True`` containing only
                complete items.
        """
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
                except Exception:
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
                    elif isinstance(self.new_object_type, type):
                        object_type_to_use = self.new_object_type
                        parameters_to_use = {}
                    else:
                        raise DAError("new_object_type must be an object type")
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
        """Trigger the gathering process for the list and return True.

        Runs the interview question loop that asks ``there_are_any``,
        creates items, and asks ``there_is_another`` until the list is
        complete. Called automatically when iterating over or measuring
        the list (unless ``auto_gather`` is False).

        Args:
            number (int, optional): Collect exactly this many items.
            item_object_type: Class to use when creating items; overrides
                ``object_type``.
            minimum (int, optional): Minimum number of items to collect.
            complete_attribute (str or list, optional): Attribute(s) that
                must be defined for an item to be considered complete.

        Returns:
            bool: Always True once gathering is complete.
        """
        # logmessage("Gather")
        if hasattr(self, 'gathered') and self.gathered:
            if self.auto_gather and len(self.elements) == 0 and hasattr(self, 'there_are_any') and self.there_are_any:
                del self.gathered
            else:
                return True
        if item_object_type is None and self.object_type is not None and not self.ask_object_type:
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
        """Return the list items as a comma-separated string with "and" before the last.

        Returns:
            str: Human-readable enumeration such as "Alice, Bob, and Carol".
        """
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
            raise DAError("Attempt to fill up " + self.instanceName + " with index " + index)
        if index < 0 and len(self.elements) + index < 0:
            num_to_add = (-1 * index) - len(self.elements)
            if num_to_add > 10:
                raise DAError("Attempt to fill up more than 10 items")
            for i in range(0, num_to_add):  # pylint: disable=unused-variable
                if self.object_type is None or self.ask_object_type:
                    self.elements.append(None)
                else:
                    self.appendObject(self.object_type, **self.object_type_parameters)
        elif len(self.elements) <= index:
            num_to_add = 1 + index - len(self.elements)
            if num_to_add > 10:
                raise DAError("Attempt to fill up more than 10 items")
            for i in range(0, num_to_add):
                if self.object_type is None or self.ask_object_type:
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

    def raise_undefined_index_error(self, index):
        var_name = object.__getattribute__(self, 'instanceName') + '[' + str(index) + ']'
        raise DAIndexError("name '" + var_name + "' is not defined")

    def __str__(self):
        self._trigger_gather()
        return str(self.comma_and_list())

    def __repr__(self):
        self._trigger_gather()
        return repr(self.elements)

    def union(self, other_set):
        """Return the union of this list (as a set) and another collection.

        Args:
            other_set: Any iterable or DASet to union with.

        Returns:
            DASet: Elements from either this list or ``other_set``.
        """
        self._trigger_gather()
        return DASet(elements=set(self.elements).union(setify(other_set)))

    def intersection(self, other_set):
        """Return elements present in both this list (as a set) and another collection.

        Args:
            other_set: Any iterable or DASet to intersect with.

        Returns:
            DASet: Elements that appear in both this list and ``other_set``.
        """
        self._trigger_gather()
        return DASet(elements=set(self.elements).intersection(setify(other_set)))

    def difference(self, other_set):
        """Return elements in this list (as a set) that are not in another collection.

        Args:
            other_set: Any iterable or DASet to subtract.

        Returns:
            DASet: Elements present in this list but not in ``other_set``.
        """
        self._trigger_gather()
        return DASet(elements=set(self.elements).difference(setify(other_set)))

    def isdisjoint(self, other_set):
        """Return True if this list and another collection share no elements.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if there is no overlap; False otherwise.
        """
        self._trigger_gather()
        return set(self.elements).isdisjoint(setify(other_set))

    def issubset(self, other_set):
        """Return True if every element of this list is also in another collection.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if this list is a subset of ``other_set``; False
                otherwise.
        """
        self._trigger_gather()
        return set(self.elements).issubset(setify(other_set))

    def issuperset(self, other_set):
        """Return True if every element of another collection is in this list.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if ``other_set`` is a subset of this list; False
                otherwise.
        """
        self._trigger_gather()
        return set(self.elements).issuperset(setify(other_set))

    def pronoun_possessive(self, target, **kwargs):
        """Return a possessive pronoun phrase for the list followed by the target.

        Delegates to the single element when the list has exactly one item.
        For multiple elements returns "their <target>" (third person), "our
        <target>" (first person), or "your <target>" (second person).

        Args:
            target (str): The possessed noun phrase (e.g., ``"fish"``).
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: Possessive phrase such as "their fish" or "her fish".
        """
        if self.number() == 1:
            self._trigger_gather()
            if isinstance(self.elements[0], DAObject):
                return self.elements[0].pronoun_possessive(target, **kwargs)
            return its(target, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            output = docassemble.base.functions.your_plural(target, **kwargs)
        elif person in ('1', '1p'):
            output = docassemble.base.functions.our_possessive(target, **kwargs)
        else:
            output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun(self, **kwargs):
        """Return an objective pronoun appropriate for the list.

        Returns "them" for multiple elements, or delegates to the single
        element for a one-item list.

        Args:
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: A pronoun such as "them", "her", "him", "you", or "us".
        """
        if self.number() == 1:
            self._trigger_gather()
            if isinstance(self.elements[0], DAObject):
                return self.elements[0].pronoun(**kwargs)
            return docassemble.base.functions.it_objective(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            output = docassemble.base.functions.you_objective_plural(**kwargs)
        elif person in ('1', '1p'):
            output = docassemble.base.functions.us_objective(**kwargs)
        else:
            output = docassemble.base.functions.them_objective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

    def pronoun_subjective(self, **kwargs):
        """Return a subjective pronoun appropriate for the collection.

        Returns "they" for multiple elements, or delegates to the single
        element for a one-item collection.

        Args:
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: A pronoun such as "they", "she", "he", "you", or "we".
        """
        if self.number() == 1:
            self._trigger_gather()
            if isinstance(self.elements[0], DAObject):
                return self.elements[0].pronoun_subjective(**kwargs)
            docassemble.base.functions.it_subjective(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            output = docassemble.base.functions.you_subjective_plural(**kwargs)
        elif person in ('1', '1p'):
            output = docassemble.base.functions.we_subjective(**kwargs)
        else:
            output = docassemble.base.functions.they_subjective(**kwargs)
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

    def _reorder_buttons(self, classes, index):
        return '<span class="text-nowrap"><a href="#" role="button" class="' + classes + '" data-tablename="' + myb64quote(self.instanceName) + '" data-tableitem="' + str(index) + '" title=' + json.dumps(word("Reorder by moving up")) + '><i class="fa-solid fa-arrow-up"></i><span class="visually-hidden">' + word("Move up") + '</span></a> <a href="#" role="button" class="btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('reorder', 'info') + ' btn-darevisit databledown"><i class="fa-solid fa-arrow-down" title=' + json.dumps(word("Reorder by moving down")) + '></i><span class="visually-hidden">' + word("Move down") + '</span></a></span> '

    def _edit_button(self, url, classes):
        return f'<a href="{url}" role="button" class="{classes}"><span class="text-nowrap"><i class="fa-solid fa-pencil-alt"></i> {word("Edit")}</span></a> '

    def _delete_button(self, url, classes):
        return f'<a href="{url}" role="button" class="{classes}"><span class="text-nowrap"><i class="fa-solid fa-trash"></i> {word("Delete")}</span></a>'

    def item_actions(self, *pargs, **kwargs):
        """Return HTML action buttons for editing and deleting a list item.

        Args:
            *pargs: First positional argument is the item object; second is
                its index. Additional positional arguments are attribute
                paths to follow up on when editing.
            **kwargs: Accepts ``edit`` (bool), ``delete`` (bool),
                ``reorder`` (bool), ``confirm`` (bool),
                ``ensure_complete`` (bool), ``read_only_attribute`` (str),
                ``edit_url_only`` (bool), and ``delete_url_only`` (bool).

        Returns:
            str: HTML string containing edit and/or delete buttons.
        """
        the_args = list(pargs)
        item = the_args.pop(0)
        index = the_args.pop(0)
        output = ''
        if kwargs.get('reorder', False):
            output += self._reorder_buttons('btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('reorder', 'info') + ' btn-darevisit datableup', index)
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
            #    items += [{'action': '_da_undefine', 'arguments': {'variables': [item.instanceName + '.' + self.complete_attribute]}})]
            if len(the_args) > 0:
                items += [{'follow up': [item.instanceName + ('' if y.startswith('[') else '.') + y for y in the_args]}]
            else:
                items += [{'follow up': [self.instanceName + '[' + repr(index) + ']']}]
            if self.complete_attribute is not None and self.complete_attribute != 'complete':
                items += [{'action': '_da_define', 'arguments': {'variables': [item.instanceName + '.' + attrib for attrib in self._complete_attributes()]}}]
            if ensure_complete:
                items += [{'action': '_da_list_ensure_complete', 'arguments': {'group': self.instanceName}}]
            output += self._edit_button(docassemble.base.functions.url_action('_da_list_edit', items=items), 'btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('edit', 'secondary') + ' btn-darevisit')
        if use_delete and can_delete:
            if kwargs.get('confirm', False):
                areyousure = ' daremovebutton'
            else:
                areyousure = ''
            output += self._delete_button(docassemble.base.functions.url_action('_da_list_remove', list=self.instanceName, item=repr(index)), 'btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('delete', 'danger') + ' btn-darevisit' + areyousure)
        if kwargs.get('edit_url_only', False):
            return docassemble.base.functions.url_action('_da_list_edit', items=items)
        if kwargs.get('delete_url_only', False):
            return docassemble.base.functions.url_action('_da_list_remove', dict=self.instanceName, item=repr(index))
        return output

    def _add_action_button(self, url, classes, icon, the_message):
        if icon != '':
            icon = f'<i class="{icon}"></i> '
        return f'<a href="{url}" class="{classes}">{icon}{the_message}</a>'

    def add_action(self, label=None, message=None, url_only=False, icon='plus-circle', color=None, size='sm', block=None, classname=None):  # pylint: disable=redefined-outer-name
        """Return HTML for a button that adds a new item to the list.

        Args:
            label (str, optional): Button label text. Defaults to "Add an item"
                or "Add another" depending on whether items already exist.
            message (str, optional): Deprecated alias for ``label``.
            url_only (bool): If True, return only the action URL instead of
                the full button HTML. Defaults to False.
            icon (str): Font Awesome icon class name. Defaults to
                ``'plus-circle'``.
            color (str, optional): Bootstrap color name. Defaults to the
                configured ``'add'`` button color.
            size (str): Button size: ``'sm'``, ``'md'``, or ``'lg'``.
                Defaults to ``'sm'``.
            block (bool, optional): If True, add ``btn-block`` class.
            classname (str, optional): Extra CSS class(es) to add.

        Returns:
            str: HTML anchor element or URL string.
        """
        if color is None:
            color = server.daconfig['button colors'].get('add', 'secondary')
        if color not in ('primary', 'secondary', 'tertiary', 'success', 'danger', 'warning', 'info', 'light', 'dark'):
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
                icon = 'fa-solid fa-' + icon
            icon = re.sub(r'^fas ', 'fa-solid ', icon)
            icon = re.sub(r'^far ', 'fa-regular ', icon)
            icon = re.sub(r'^fab ', 'fa-brands ', icon)
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
        the_url = docassemble.base.functions.url_action('_da_list_add', list=self.instanceName)
        if url_only:
            return the_url
        return self._add_action_button(the_url, 'btn' + size + block + ' ' + server.button_class_prefix + color + ' btn-darevisit' + classname, icon, message)

    def hook_on_gather(self, *pargs, **kwargs):
        """Override this method to run code just before the list is marked as gathered."""

    def hook_after_gather(self, *pargs, **kwargs):
        """Override this method to run code just after the list is marked as gathered."""

    def hook_on_item_complete(self, item, *pargs, **kwargs):
        """Override this method to run code when an item becomes complete.

        Args:
            item: The item that has just been marked complete.
        """

    def hook_on_remove(self, item, *pargs, **kwargs):
        """Override this method to run code when an item is removed from the list.

        Args:
            item: The item being removed.
        """

    def __eq__(self, other):
        self._trigger_gather()
        return self.elements == other

    def __hash__(self):
        return hash((self.instanceName,))


class DADict(DAObject):
    """A dictionary that docassemble can populate through interview questions.

    DADict behaves like a Python dictionary, but docassemble can ask questions
    to define entries. The gathering process is analogous to DAList, using
    ``there_are_any`` and ``there_is_another`` to determine when the dictionary
    is complete.

    Attributes:
        elements (dict): The underlying Python dictionary of items.
        gathered (bool): True when all entries have been gathered.
        auto_gather (bool): If True (the default), gathering is triggered
            automatically.
        object_type: A DAObject subclass (or ``.using()`` result) used when
            creating new values via ``initializeObject()``. Defaults to None.
        complete_attribute (str or None): An attribute that must be defined on
            each value before it is considered complete.
        there_are_any (bool): Whether any entries exist.
        there_is_another (bool): Whether there is another entry to add.
    """

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
                self.object_type = None
                self.object_type_parameters = {}
            else:
                self.ask_object_type = False
            del kwargs['ask_object_type']
        if not hasattr(self, 'ask_object_type'):
            self.ask_object_type = False
        if 'keys' in kwargs:
            if isinstance(kwargs['keys'], (DAList, DASet, abc.Iterable)) and not isinstance(kwargs['keys'], str):
                self.new(kwargs['keys'])
            del kwargs['keys']
        super().init(*pargs, **kwargs)

    def set_object_type(self, object_type):
        """Set the object type used when creating new dictionary values.

        Args:
            object_type: A class or ``.using()`` result to use when
                ``initializeObject()`` creates new values.
        """
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
        """Return the variable name for a dictionary entry by its key.

        Args:
            item: The key of the entry.

        Returns:
            str: Variable name such as ``'mydict["foo"]'``, suitable for use
                in ``force_ask()`` and similar functions.
        """
        return self.instanceName + '[' + repr(item) + ']'

    def delitem(self, *pargs):
        """Delete entries by key.

        Args:
            *pargs: Keys of entries to delete. Keys not in the dictionary
                are silently ignored.
        """
        for item in pargs:
            if item in self.elements:
                del self[item]

    def invalidate_item(self, *pargs):
        """Invalidate one or more entries so they are re-evaluated.

        Args:
            *pargs: Keys of entries to invalidate.
        """
        for item in pargs:
            if item in self.elements.keys():
                invalidate(self.item_name(item))

    def getitem_fresh(self, item):
        """Recompute and return the value for the given key, bypassing the cache.

        Args:
            item: The dictionary key to recompute.

        Returns:
            object: The freshly computed value for ``item``.
        """
        if item in self.elements:
            docassemble.base.functions.reconsider(self.item_name(item))
        return self[item]

    def all_false(self, *pargs, **kwargs):
        """Return True if all (or all specified) values are falsy.

        Args:
            *pargs: Optional keys or iterables of keys to check. If omitted,
                all keys are checked.
            **kwargs: Accepts ``exclusive`` (bool). When True, returns True
                only if the specified keys are the only falsy values.

        Returns:
            bool: True if all values for the specified (or all) keys are
                falsy; False otherwise.
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
        """Return True if at least one (or one specified) value is truthy.

        Args:
            *pargs: Optional keys or iterables of keys to check.
            **kwargs: Passed through to ``all_false()``.

        Returns:
            bool: True if any value is truthy; False otherwise.
        """
        return not self.all_false(*pargs, **kwargs)

    def any_false(self, *pargs, **kwargs):
        """Return True if at least one (or one specified) value is falsy.

        Args:
            *pargs: Optional keys or iterables of keys to check.
            **kwargs: Passed through to ``all_true()``.

        Returns:
            bool: True if any value is falsy; False otherwise.
        """
        return not self.all_true(*pargs, **kwargs)

    def all_true(self, *pargs, **kwargs):
        """Return True if all (or all specified) values are truthy.

        Args:
            *pargs: Optional keys or iterables of keys to check. If omitted,
                all keys are checked.
            **kwargs: Accepts ``exclusive`` (bool). When True, returns True
                only if the specified keys are the only truthy values.

        Returns:
            bool: True if all values for the specified (or all) keys are
                truthy; False otherwise.
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
        """Return a DAList of keys whose values are truthy.

        Args:
            insertion_order (bool): If True, preserve insertion order instead
                of sorting. Defaults to False.

        Returns:
            DAList: Keys whose associated values are truthy.
        """
        if insertion_order:
            return DAList(elements=[key for key, value in self.items() if value])
        return DAList(elements=[key for key, value in self._sorted_items() if value])

    def false_values(self, insertion_order=False):
        """Return a DAList of keys whose values are falsy.

        Args:
            insertion_order (bool): If True, preserve insertion order instead
                of sorting. Defaults to False.

        Returns:
            DAList: Keys whose associated values are falsy.
        """
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
        """Create a new object and store it at the given key in the dictionary.

        Args:
            *pargs: First positional argument is the dictionary key to set.
                An optional second positional argument is the class (or
                ``.using()`` result) for the new object. Falls back to
                ``object_type``, then ``new_object_type`` (when
                ``ask_object_type`` is True), then ``DAObject``.
            **kwargs: Additional keyword arguments passed to the new object's
                constructor.

        Returns:
            DAObject: The newly created object stored at ``self[entry]``.
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
            if self.ask_object_type:
                if isinstance(self.new_object_type, DAObjectPlusParameters):
                    objectFunction = self.new_object_type.object_type
                    new_obj_parameters = self.new_object_type.parameters
                elif isinstance(self.new_object_type, type):
                    objectFunction = self.new_object_type
                else:
                    raise DAError("new_object_type must be an object type")
            elif self.object_type is not None:
                objectFunction = self.object_type
                for key, val in self.object_type_parameters.items():
                    new_obj_parameters[key] = val
            else:
                objectFunction = DAObject
        for key, val in kwargs.items():
            new_obj_parameters[key] = val
        newobject = objectFunction(self.instanceName + '[' + repr(entry) + ']', *pargs, **new_obj_parameters)
        self[entry] = newobject
        self.there_are_any = True
        if objectFunction is None and self.ask_object_type and hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        return newobject

    def new(self, *pargs, **kwargs):
        """Initialize new dictionary entries as DAObject instances.

        For each key provided, creates an object of ``object_type`` (or
        ``DAObject`` if not set) and stores it under that key if the key does
        not already exist. Iterables in ``pargs`` are flattened automatically.

        Args:
            *pargs: Keys (or iterables of keys) for which to create new
                objects.
            **kwargs: Keyword arguments passed to each new object's
                constructor.
        """
        for parg in pargs:
            if isinstance(parg, (DAList, DASet, abc.Iterable)) and not isinstance(parg, str):
                for item in parg:
                    self.new(item, **kwargs)
            else:
                new_obj_parameters = {}
                if self.ask_object_type:
                    if parg not in self.elements:
                        self[parg] = None
                    continue
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
        """Reset the gathered state so the collection will be re-gathered.

        Args:
            recursive (bool): If True, also reset gathering on nested DAList
                and DADict objects within the collection. Defaults to False.
            only_if_empty (bool): If True, only reset if the collection is
                empty. Defaults to False.
            mark_incomplete (bool): If True, delete the ``complete_attribute``
                on each item so items are treated as incomplete. Defaults to
                False.
        """
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
        """Return a shallow copy of the dictionary restricted to the given keys.

        Args:
            *pargs: Keys to include in the result. A single callable argument
                is treated as a filter function ``f(value) -> bool``.

        Returns:
            DADict: A new DADict with ``gathered=True`` containing only the
                specified keys and their values.
        """
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
        """Return True if the gathering process for this dictionary has completed.

        Returns:
            bool: True if the dictionary has been gathered; False otherwise.
        """
        if hasattr(self, 'gathered'):
            return True
        if hasattr(self, 'was_gathered') and self.was_gathered:
            return True
        return False

    def itself(self, **kwargs):
        """Returns "themselves" unless the dictionary has only one element,
        in which case the method is called on the first element."""
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements.values())[0]
            if isinstance(first_element, DAObject):
                return first_element.itself(**kwargs)
            return docassemble.base.functions.itself(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.yourselves(**kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.ourselves(**kwargs)
        return docassemble.base.functions.themselves(**kwargs)

    def do_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "do x eat" if there is
        more than one element. x is the string representation of the
        dictionary. If there is only one element, the method is called on
        the first element of the dictionary.

        """
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements.values())[0]
            if isinstance(first_element, DAObject):
                return first_element.do_question(**kwargs)
            return does_a_b(first_element, the_verb, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.do_you_plural(the_verb, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.do_we(the_verb, **kwargs)
        return docassemble.base.functions.do_a_b(self, the_verb, **kwargs)

    def did_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "did x eat" if there is
        more than one element. x is the string representation of the
        dictionary. If there is only one element, the method is called on
        the first element of the dictionary.

        """
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements.values())[0]
            if isinstance(first_element, DAObject):
                return first_element.did_question(the_verb, **kwargs)
            return did_a_b(first_element, the_verb, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.did_you_plural(the_verb, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.did_we(the_verb, **kwargs)
        return docassemble.base.functions.did_a_b_plural(self, the_verb, **kwargs)

    def were_question(self, the_target, **kwargs):
        """Given a target like "married", returns "were x married" if
        there is more than one element in the dictionary. x is the
        string representation of the dictionary. If there is only one
        element, the method is called on the first element.

        """
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements.values())[0]
            if isinstance(first_element, DAObject):
                return first_element.were_question(the_target, **kwargs)
            return was_a_b(first_element, the_target, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.were_you_plural(the_target, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.were_we(the_target, **kwargs)
        return docassemble.base.functions.were_a_b_plural(self, the_target, **kwargs)

    def have_question(self, the_target, **kwargs):
        """Given a target like "married", returns "have x married" if
        there is more than one element in the dictionary. x is the
        string representation of the dictionary. If there is only one
        element, the method is called on the first element.

        """
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements.values())[0]
            if isinstance(first_element, DAObject):
                return first_element.have_question(the_target, **kwargs)
            return has_a_b(first_element, the_target, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.have_you_plural(the_target, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.have_we(the_target, **kwargs)
        return docassemble.base.functions.have_a_b(self, the_target, **kwargs)

    def does_verb(self, the_verb, **kwargs):
        """Return the correctly conjugated present-tense form of a verb for the dictionary.

        Args:
            the_verb (str): The base form of the verb (e.g., ``"finish"``).
            **kwargs: Accepts ``person`` (str), ``language`` (str), ``past``
                (bool), and ``present`` (bool) for tense control.

        Returns:
            str: Conjugated verb, e.g. "finishes" for one player or "finish"
                for multiple players.
        """
        language = kwargs.get('language', None)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if ('past' in kwargs and kwargs['past'] is True) or ('present' in kwargs and kwargs['present'] is False):
            if self.number() > 1:
                if person in ('2', '2p'):
                    tense = '2ppl'
                elif person in ('1', '1p'):
                    tense = '1ppl'
                else:
                    tense = '3ppl'
            else:
                if person == '2':
                    tense = '2sgp'
                elif person == '2p':
                    tense = '2ppl'
                elif person == '1':
                    tense = '1sgp'
                elif person == '1p':
                    tense = '1ppl'
                else:
                    tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
        if self.number() > 1:
            if person in ('2', '2p'):
                tense = '2pl'
            elif person in ('1', '1p'):
                tense = '1pl'
            else:
                tense = '3pl'
        else:
            if person == '2':
                tense = '2sg'
            elif person == '2p':
                tense = '2pl'
            elif person == '1':
                tense = '1sg'
            elif person == '1p':
                tense = '1pl'
            else:
                tense = '3sg'
        return verb_present(the_verb, tense, language=language)

    def did_verb(self, the_verb, **kwargs):
        """Return the correctly conjugated past-tense form of a verb for the collection.

        Args:
            the_verb (str): The base form of the verb (e.g., ``"sue"``).
            **kwargs: Accepts ``person`` (str) and ``language`` (str).

        Returns:
            str: Past-tense conjugated verb, e.g. "sued".
        """
        language = kwargs.get('language', None)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if self.number() > 1:
            if person in ('2', '2p'):
                tense = '2ppl'
            elif person in ('1', '1p'):
                tense = '1ppl'
            else:
                tense = '3ppl'
        else:
            if person == '2':
                tense = '2sgp'
            elif person == '2p':
                tense = '2ppl'
            elif person == '1':
                tense = '1sgp'
            elif person == '1p':
                tense = '1ppl'
            else:
                tense = '3sgp'
        return verb_past(the_verb, tense, language=language)

    def as_singular_noun(self):
        """Return the singular noun form derived from the dictionary's instance name.

        E.g., ``player.as_singular_noun()`` returns ``"player"`` regardless
        of how many players are in the dictionary.

        Returns:
            str: Singular noun form of the trailing part of the instance name.
        """
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun

    def quantity_noun(self, *pargs, **kwargs):
        """Return a noun phrase combining the number of entries with the noun.

        Args:
            *pargs: Passed to the ``quantity_noun()`` function after the count.
            **kwargs: Passed through to ``quantity_noun()``.

        Returns:
            str: Phrase such as "3 players".
        """
        the_args = [self.number()] + list(pargs)
        return quantity_noun(*the_args, **kwargs)

    def as_noun(self, *pargs, **kwargs):
        """Return a singular or plural noun form for the dictionary, derived from the instance name.

        E.g., ``player.as_noun()`` returns ``"player"`` or ``"players"``
        depending on how many entries are in the dictionary.

        Args:
            *pargs: If provided, the first argument overrides the noun instead
                of using the instance name.
            **kwargs: Accepts ``plural`` (bool), ``singular`` (bool),
                ``article`` (bool), ``some`` (bool), ``this`` (bool),
                ``capitalize`` (bool), and ``language`` (str).

        Returns:
            str: Noun form with optional article.
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
            return capitalize_func(output)
        return output

    def possessive(self, target, **kwargs):
        """Return a possessive phrase using the dictionary's noun form and the target.

        Args:
            target (str): The possessed noun phrase (e.g., ``"fish"``).
            **kwargs: Passed to ``possessify()``; may include ``language``.

        Returns:
            str: E.g., "player's score" (one entry) or "players' scores"
                (multiple entries).
        """
        language = kwargs.get('language', None)
        return possessify(self.as_noun(**kwargs), target, plural=(self.number() > 1), language=language)

    def number(self):
        """Return the number of entries in the dictionary, triggering gathering if needed.

        Returns:
            int: Count of keys in the dictionary.
        """
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return len(self.elements)

    def gathering_started(self):
        """Return True if any items have been gathered or ``there_are_any`` has been set.

        Returns:
            bool: True if gathering has started; False otherwise.
        """
        if hasattr(self, 'gathered') or hasattr(self, 'there_are_any') or len(self.elements) > 0:
            return True
        return False

    def number_gathered(self, if_started=False):
        """Returns the number of elements in the dictionary that have been gathered so far."""
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
        items = self.__class__(self.instanceName)
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
                except Exception:
                    continue
            items[key] = val
        items.gathered = True
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
                        raise DAError("new_object_type must be an object type")
                    self[key] = object_type_to_use(self.instanceName + '[' + repr(key) + ']', **parameters_to_use)
            if hasattr(self, 'new_object_type'):
                delattr(self, 'new_object_type')
        for key in keys:
            elem = self.elements[key]
            if item_object_type is not None and complete_attribute is not None:
                for attrib in self._complete_attributes(complete_attribute):
                    complex_getattr(elem, attrib)
            else:
                str(elem)

    def cancel_add_or_edit(self):
        unique_id = docassemble.base.functions.this_thread.current_info['user']['session_uid']
        if 'event_stack' in docassemble.base.functions.this_thread.internal and unique_id in docassemble.base.functions.this_thread.internal['event_stack']:
            new_stack = []
            for item in docassemble.base.functions.this_thread.internal['event_stack'][unique_id]:
                if 'arguments' in item:
                    if 'dict' in item['arguments'] and item['arguments']['dict'] == self.instanceName:
                        continue
                    if 'group' in item['arguments'] and item['arguments']['group'] == self.instanceName:
                        continue
                if 'action' in item and item['action'].startswith(self.instanceName + '['):
                    continue
                new_stack.append(item)
            docassemble.base.functions.this_thread.internal['event_stack'][unique_id] = new_stack
        if self.complete_elements().number() < self.number_gathered():
            self.popitem()
        self.delattr('doing_gathered_and_complete', 'there_is_one_other', 'new_item_name')

    def gathered_and_complete(self):
        """Ensure every value in the dictionary is complete and return True.

        Returns:
            bool: Always True once all values are complete.
        """
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
        """Trigger the gathering process for the dictionary and return True.

        Args:
            item_object_type: Class to use when creating values; overrides
                ``object_type``.
            number (int, optional): Collect exactly this many entries.
            minimum (int, optional): Minimum number of entries to collect.
            complete_attribute (str or list, optional): Attribute(s) that
                must be defined for a value to be considered complete.
            keys (list, optional): Specific keys to validate.

        Returns:
            bool: Always True once gathering is complete.
        """
        if hasattr(self, 'gathered') and self.gathered:
            if self.auto_gather and len(self.elements) == 0 and hasattr(self, 'there_are_any') and self.there_are_any:
                del self.gathered
            else:
                return True
        if not self.auto_gather:
            return self.gathered
        if item_object_type is None and self.object_type is not None and not self.ask_object_type:
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
        should_break_out = False
        while not should_break_out and ((number is not None and len(self.elements) < int(number)) or (minimum is not None and len(self.elements) < int(minimum)) or (self.ask_number is False and minimum != 0 and (self.there_is_another or (hasattr(self, 'there_is_one_other') and self.there_is_one_other)))):
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
                    self[self.new_item_name] = self.new_item_value
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
                    should_break_out = True
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
            if (self.object_type is not None or self.ask_object_type) and self.complete_attribute is not None:
                for attrib in self._complete_attributes():
                    complex_getattr(elem, attrib)
            else:
                str(elem)

    def comma_and_list(self, **kwargs):
        """Return the dictionary keys as a comma-separated string with "and" before the last.

        Returns:
            str: Human-readable enumeration of keys such as "alpha, beta, and gamma".
        """
        self._trigger_gather()
        try:
            return comma_and_list(self._sorted_elements_keys(), **kwargs)
        except TypeError:
            return comma_and_list(self.elements.keys(), **kwargs)

    def __getitem__(self, index):
        if index not in self.elements:
            if (self.object_type is None and not self.ask_object_type) or docassemble.base.functions.this_thread.probing:
                var_name = object.__getattribute__(self, 'instanceName') + "[" + repr(index) + "]"
                raise DAIndexError("name '" + var_name + "' is not defined")
            if self.ask_object_type:
                self[index] = None
            else:
                self.initializeObject(index, self.object_type, **self.object_type_parameters)
            return self.elements[index]
        return self.elements[index]

    def raise_undefined_index_error(self, index):
        var_name = object.__getattribute__(self, 'instanceName') + "[" + repr(index) + "]"
        raise DAIndexError("name '" + var_name + "' is not defined")

    def __setitem__(self, key, the_value):
        self.elements[key] = the_value

    def __contains__(self, item):
        self._trigger_gather()
        return self.elements.__contains__(item)

    def keys(self):
        """Return the keys of the dictionary as a sorted list, triggering gathering.

        Returns:
            list: Sorted list of keys.
        """
        self._trigger_gather()
        try:
            return self._sorted_elements_keys()
        except TypeError:
            return list(self.elements.keys())

    def values(self):
        """Return the values of the dictionary, triggering gathering.

        Returns:
            dict_values: The underlying dictionary's values view.
        """
        self._trigger_gather()
        return self.elements.values()

    def update(self, *pargs, **kwargs):
        """Update the dictionary with the keys and values of another mapping.

        Args:
            *pargs: An optional first positional argument is a dict or DADict
                whose entries are merged in.
            **kwargs: Additional key/value pairs to merge.
        """
        if len(pargs) > 0:
            other_dict = pargs[0]
            if isinstance(other_dict, DADict):
                self.elements.update(other_dict.elements)
        self.elements.update(*pargs, **kwargs)

    def pop(self, *pargs):
        """Remove a key and return its value.

        Args:
            *pargs: First argument is the key to remove; an optional second
                argument is the default value when the key is absent.

        Returns:
            object: The value associated with the removed key.
        """
        if pargs[0] in self.elements:
            self.hook_on_remove(self.elements[pargs[0]])
        if len(self.elements) == 1:
            self.there_are_any = False
        return self.elements.pop(*pargs)

    def popitem(self):
        """Remove and return an arbitrary (key, value) pair.

        Returns:
            tuple: A ``(key, value)`` pair removed from the dictionary.
        """
        if len(self.elements) == 1:
            self.there_are_any = False
        return self.elements.popitem()

    def setdefault(self, *pargs):
        """Return the value for a key, inserting a default if the key is absent.

        Args:
            *pargs: First argument is the key; optional second argument is
                the default value (defaults to None).

        Returns:
            object: The existing or newly set value for the key.
        """
        return self.elements.setdefault(*pargs)

    def get(self, *pargs, **kwargs):
        """Return the value for a key, or a default if the key is absent.

        Args:
            *pargs: First argument is the key; optional second argument is
                the default (defaults to None).

        Returns:
            object: Value for the key, or the default.
        """
        return self.elements.get(*pargs, **kwargs)

    def clear(self):
        """Removes all the items from the dictionary."""
        return self.elements.clear()

    def copy(self):
        """Returns a copy of the dictionary."""
        return self.elements.copy()

    def has_key(self, key):
        """Return True if the key exists in the dictionary.

        Args:
            key: The key to test.

        Returns:
            bool: True if ``key`` is present; False otherwise.
        """
        return key in self.elements

    def item(self, key):
        """Return the value for a key, or a blank DAEmpty if the key does not exist.

        Args:
            key: The dictionary key to look up.

        Returns:
            object: The value for ``key``, or a ``DAEmpty`` instance.
        """
        self._trigger_gather()
        if key in self.elements:
            return self[key]
        return DAEmpty()

    def items(self):
        """Return the items of the dictionary, triggering gathering.

        Returns:
            dict_items: Key/value pairs view of the underlying dictionary.
        """
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
        """Return the union of this dictionary's values (as a set) and another collection.

        Args:
            other_set: Any iterable or DASet to union with.

        Returns:
            DASet: Values from either this dictionary or ``other_set``.
        """
        self._trigger_gather()
        return DASet(elements=set(self.elements.values()).union(setify(other_set)))

    def intersection(self, other_set):
        """Return values present in both this dictionary and another collection.

        Args:
            other_set: Any iterable or DASet to intersect with.

        Returns:
            DASet: Values that appear in both this dictionary and ``other_set``.
        """
        self._trigger_gather()
        return DASet(elements=set(self.elements.values()).intersection(setify(other_set)))

    def difference(self, other_set):
        """Return values in this dictionary that are not in another collection.

        Args:
            other_set: Any iterable or DASet to subtract.

        Returns:
            DASet: Values in this dictionary but not in ``other_set``.
        """
        self._trigger_gather()
        return DASet(elements=set(self.elements.values()).difference(setify(other_set)))

    def isdisjoint(self, other_set):
        """Return True if this dictionary's values and another collection share no elements.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if there is no overlap; False otherwise.
        """
        self._trigger_gather()
        return set(self.elements.values()).isdisjoint(setify(other_set))

    def issubset(self, other_set):
        """Return True if every value in this dictionary is also in another collection.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if this dictionary's values are a subset of ``other_set``.
        """
        self._trigger_gather()
        return set(self.elements.values()).issubset(setify(other_set))

    def issuperset(self, other_set):
        """Return True if every element of another collection is in this dictionary's values.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if ``other_set`` is a subset of this dictionary's
                values; False otherwise.
        """
        self._trigger_gather()
        return set(self.elements.values()).issuperset(setify(other_set))

    def pronoun_possessive(self, target, **kwargs):
        """Return a possessive pronoun phrase for the collection followed by the target.

        Args:
            target (str): The possessed noun phrase (e.g., ``"fish"``).
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: Possessive phrase such as "their fish".
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = your(target, **kwargs)
        elif person == '2p':
            output = docassemble.base.functions.your_plural(target, **kwargs)
        elif person == '1':
            output = docassemble.base.functions.my_possessive(target, **kwargs)
        elif person == '1p':
            output = docassemble.base.functions.our_possessive(**kwargs)
        else:
            output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun(self, **kwargs):
        """Return an objective pronoun appropriate for the dictionary.

        Returns "them" for multiple values, or delegates to the single
        value for a one-item dictionary.

        Args:
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: A pronoun such as "them", "her", "him", "you", or "us".
        """
        if self.number() == 1:
            self._trigger_gather()
            if isinstance(list(self.elements.values())[0], DAObject):
                return list(self.elements.values())[0].pronoun(**kwargs)
            return docassemble.base.functions.it_objective(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            output = docassemble.base.functions.you_objective_plural(**kwargs)
        elif person in ('1', '1p'):
            output = docassemble.base.functions.us_objective(**kwargs)
        else:
            output = docassemble.base.functions.them_objective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

    def pronoun_subjective(self, **kwargs):
        """Return a subjective pronoun appropriate for the collection.

        Returns "they" for multiple elements, or delegates to the single
        element for a one-item collection.

        Args:
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: A pronoun such as "they", "she", "he", "you", or "we".
        """
        if self.number() == 1:
            self._trigger_gather()
            if isinstance(list(self.elements.values())[0], DAObject):
                return list(self.elements.values())[0].pronoun_subjective(**kwargs)
            docassemble.base.functions.it_subjective(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            output = docassemble.base.functions.you_subjective_plural(**kwargs)
        elif person in ('1', '1p'):
            output = docassemble.base.functions.we_subjective(**kwargs)
        else:
            output = docassemble.base.functions.they_subjective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def _edit_button(self, url, classes):
        return f'<a href="{url}" role="button" class="{classes}"><span class="text-nowrap"><i class="fa-solid fa-pencil-alt"></i> {word("Edit")}</span></a> '

    def _delete_button(self, url, classes):
        return f'<a href="{url}" role="button" class="{classes}"><span class="text-nowrap"><i class="fa-solid fa-trash"></i> {word("Delete")}</span></a>'

    def item_actions(self, *pargs, **kwargs):
        """Return HTML action buttons for editing and deleting a dictionary entry.

        Args:
            *pargs: First positional argument is the value object; second is
                its key. Additional positional arguments are attribute paths
                to follow up on when editing.
            **kwargs: Accepts ``edit`` (bool), ``delete`` (bool),
                ``confirm`` (bool), ``ensure_complete`` (bool),
                ``read_only_attribute`` (str), ``edit_url_only`` (bool),
                and ``delete_url_only`` (bool).

        Returns:
            str: HTML string containing edit and/or delete buttons.
        """
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
                items += [{'action': '_da_undefine', 'arguments': {'variables': [item.instanceName + '.complete']}}]
            if len(the_args) > 0:
                items += [{'follow up': [item.instanceName + ('' if y.startswith('[') else '.') + y for y in the_args]}]
            else:
                items += [{'follow up': [self.instanceName + '[' + repr(index) + ']']}]
            if self.complete_attribute is not None and self.complete_attribute != 'complete':
                items += [{'action': '_da_define', 'arguments': {'variables': [item.instanceName + '.' + attrib for attrib in self._complete_attributes()]}}]
            if ensure_complete:
                items += [{'action': '_da_dict_ensure_complete', 'arguments': {'group': self.instanceName}}]
            output += self._edit_button(docassemble.base.functions.url_action('_da_dict_edit', items=items), 'btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('edit', 'secondary') + ' btn-darevisit')
        if use_delete and can_delete:
            if kwargs.get('confirm', False):
                areyousure = ' daremovebutton'
            else:
                areyousure = ''
            output += self._delete_button(docassemble.base.functions.url_action('_da_dict_remove', dict=self.instanceName, item=repr(index)), 'btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('delete', 'danger') + ' btn-darevisit' + areyousure)
        if kwargs.get('edit_url_only', False):
            return docassemble.base.functions.url_action('_da_dict_edit', items=items)
        if kwargs.get('delete_url_only', False):
            return docassemble.base.functions.url_action('_da_dict_remove', dict=self.instanceName, item=repr(index))
        return output

    def _add_action_button(self, url, classes, icon, the_message):
        if icon != '':
            icon = f'<i class="{icon}"></i> '
        return f'<a href="{url}" class="{classes}">{icon}{the_message}</a>'

    def add_action(self, label=None, message=None, url_only=False, icon='plus-circle', color=None, size='sm', block=None, classname=None):  # pylint: disable=redefined-outer-name
        """Returns HTML for adding an item to a dict"""
        if color is None:
            color = server.daconfig['button colors'].get('add', 'secondary')
        if color not in ('primary', 'secondary', 'tertiary', 'success', 'danger', 'warning', 'info', 'light', 'dark'):
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
                icon = 'fa-solid fa-' + icon
            icon = re.sub(r'^fas ', 'fa-solid ', icon)
            icon = re.sub(r'^far ', 'fa-regular ', icon)
            icon = re.sub(r'^fab ', 'fa-brands ', icon)
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
        the_url = docassemble.base.functions.url_action('_da_dict_add', dict=self.instanceName)
        if url_only:
            return the_url
        return self._add_action_button(the_url, 'btn' + size + block + ' ' + server.button_class_prefix + color + ' btn-darevisit' + classname, icon, message)

    def _new_elements(self):
        return {}

    def hook_on_gather(self, *pargs, **kwargs):
        """Override this method to run code just before the dictionary is marked as gathered."""

    def hook_after_gather(self, *pargs, **kwargs):
        """Override this method to run code just after the dictionary is marked as gathered."""

    def hook_on_item_complete(self, item, *pargs, **kwargs):
        """Override this method to run code when an item becomes complete.

        Args:
            item: The item that has just been marked complete.
        """

    def hook_on_remove(self, item, *pargs, **kwargs):
        """Override this method to run code when an entry is removed from the dictionary.

        Args:
            item: The value being removed.
        """

    def __eq__(self, other):
        self._trigger_gather()
        return self.elements == other

    def __hash__(self):
        return hash((self.instanceName,))


class DAOrderedDict(DADict):
    """A DADict that preserves insertion order (backed by OrderedDict).

    Inherits all methods from DADict. Keys and items are iterated in
    insertion order rather than sorted order.
    """

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
    """A set that docassemble can populate through interview questions.

    DASet behaves like a Python set, but docassemble can ask questions to
    add members. Gathering is controlled by the same ``there_are_any`` /
    ``there_is_another`` attributes as DAList.

    Attributes:
        elements (set): The underlying Python set of items.
        gathered (bool): True when all items have been gathered.
        auto_gather (bool): If True (the default), gathering is triggered
            automatically.
        there_are_any (bool): Whether any items exist.
        there_is_another (bool): Whether there is another item to add.
    """

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
        """Ensure every item in the set is complete and return True.

        Returns:
            bool: Always True once all items are complete.
        """
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
        """Return a gathered DASet of only the complete items.

        Args:
            complete_attribute (str or list, optional): Override the set's
                own ``complete_attribute`` setting.

        Returns:
            DASet: A new DASet with ``gathered=True`` containing only
                complete items.
        """
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
                except Exception:
                    continue
            items.add(item)
        items.gathered = True
        return items

    def filter(self, *pargs, **kwargs):
        """Return a new DASet containing only items matching the given attribute values.

        Args:
            *pargs: Optional first argument sets the instance name of the
                returned set; defaults to this set's instance name.
            **kwargs: Attribute name/value pairs used to filter items.

        Returns:
            DASet: A gathered copy containing only matching items.
        """
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
        """Reset the gathered state so the collection will be re-gathered.

        Args:
            recursive (bool): If True, also reset gathering on nested DAList
                and DADict objects within the collection. Defaults to False.
            only_if_empty (bool): If True, only reset if the collection is
                empty. Defaults to False.
            mark_incomplete (bool): If True, delete the ``complete_attribute``
                on each item so items are treated as incomplete. Defaults to
                False.
        """
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
        """Return True if the gathering process for this set has completed.

        Returns:
            bool: True if the set has been gathered; False otherwise.
        """
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
        """Remove an element from the set.

        Args:
            elem: The element to remove.

        Raises:
            KeyError: If ``elem`` is not present in the set.
        """
        if elem in self.elements:
            self.hook_on_remove(elem)
        self.elements.remove(elem)
        if len(self.elements) == 0:
            self.there_are_any = False

    def discard(self, elem):
        """Remove an element from the set if it is present; do nothing otherwise.

        Args:
            elem: The element to discard.
        """
        if elem in self.elements:
            self.hook_on_remove(elem)
        self.elements.discard(elem)
        if len(self.elements) == 0:
            self.there_are_any = False

    def pop(self):
        """Remove and return an arbitrary element from the set.

        Returns:
            object: An arbitrary element removed from the set.

        Raises:
            KeyError: If the set is empty.
        """
        if len(self.elements) == 1:
            self.there_are_any = False
        return self.elements.pop()

    def add(self, *pargs):
        """Add items to the set, unpacking iterables automatically.

        Args:
            *pargs: Items to add. If an argument is a DAList, DASet, or other
                iterable (but not a string), its members are added individually.
        """
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

    def is_user(self):
        """Returns True if the set has one element and the one element is the user, otherwise False."""
        self._trigger_gather()
        if self.number() == 1:
            return list(self.elements)[0].is_user()
        return False

    def itself(self, **kwargs):
        """Returns "themselves" unless the set has only one element,
        in which case the method is called on the first element."""
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements)[0]
            if isinstance(first_element, DAObject):
                return first_element.itself(**kwargs)
            return docassemble.base.functions.itself(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.yourselves(**kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.ourselves(**kwargs)
        return docassemble.base.functions.themselves(**kwargs)

    def do_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "do x eat" if there is
        more than one element. x is the string representation of the
        set. If there is only one element, the method is called on
        the first element of the set.

        """
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements)[0]
            if isinstance(first_element, DAObject):
                return first_element.do_question(**kwargs)
            return does_a_b(first_element, the_verb, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.do_you_plural(the_verb, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.do_we(the_verb, **kwargs)
        return docassemble.base.functions.do_a_b(self, the_verb, **kwargs)

    def did_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "did x eat" if there is
        more than one element. x is the string representation of the
        set. If there is only one element, the method is called on
        the first element of the set.

        """
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements)[0]
            if isinstance(first_element, DAObject):
                return first_element.did_question(the_verb, **kwargs)
            return did_a_b(first_element, the_verb, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.did_you_plural(the_verb, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.did_we(the_verb, **kwargs)
        return docassemble.base.functions.did_a_b_plural(self, the_verb, **kwargs)

    def were_question(self, the_target, **kwargs):
        """Given a target like "married", returns "were x married" if
        there is more than one element in the set. x is the string
        representation of the set. If there is only one element, the
        method is called on the first element.

        """
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements)[0]
            if isinstance(first_element, DAObject):
                return first_element.were_question(the_target, **kwargs)
            return was_a_b(first_element, the_target, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.were_you_plural(the_target, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.were_we(the_target, **kwargs)
        return docassemble.base.functions.were_a_b_plural(self, the_target, **kwargs)

    def have_question(self, the_target, **kwargs):
        """Given a target like "married", returns "have x married" if
        there is more than one element in the set. x is the string
        representation of the set. If there is only one element, the
        method is called on the first element.

        """
        self._trigger_gather()
        if self.number() == 1:
            first_element = list(self.elements)[0]
            if isinstance(first_element, DAObject):
                return first_element.have_question(the_target, **kwargs)
            return has_a_b(first_element, the_target, **kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            return docassemble.base.functions.have_you_plural(the_target, **kwargs)
        if person in ('1', '1p'):
            return docassemble.base.functions.have_we(the_target, **kwargs)
        return docassemble.base.functions.have_a_b(self, the_target, **kwargs)

    def does_verb(self, the_verb, **kwargs):
        """Return the correctly conjugated present-tense form of a verb for the set.

        Args:
            the_verb (str): The base form of the verb (e.g., ``"finish"``).
            **kwargs: Accepts ``person`` (str), ``language`` (str), ``past``
                (bool), and ``present`` (bool) for tense control.

        Returns:
            str: Conjugated verb, e.g. "finishes" for one item or "finish"
                for multiple items.
        """
        language = kwargs.get('language', None)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if ('past' in kwargs and kwargs['past'] is True) or ('present' in kwargs and kwargs['present'] is False):
            if self.number() > 1:
                if person in ('2', '2p'):
                    tense = '2ppl'
                elif person in ('1', '1p'):
                    tense = '1ppl'
                else:
                    tense = '3ppl'
            else:
                if person == '2':
                    tense = '2sgp'
                elif person == '2p':
                    tense = '2ppl'
                elif person == '1':
                    tense = '1sgp'
                elif person == '1p':
                    tense = '1ppl'
                else:
                    tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
        if self.number() > 1:
            if person in ('2', '2p'):
                tense = '2pl'
            elif person in ('1', '1p'):
                tense = '1pl'
            else:
                tense = '3pl'
        else:
            if person == '2':
                tense = '2sg'
            elif person == '2p':
                tense = '2pl'
            elif person == '1':
                tense = '1sg'
            elif person == '1p':
                tense = '1pl'
            else:
                tense = '3sg'
        return verb_present(the_verb, tense, language=language)

    def did_verb(self, the_verb, **kwargs):
        """Return the correctly conjugated past-tense form of a verb for the collection.

        Args:
            the_verb (str): The base form of the verb (e.g., ``"sue"``).
            **kwargs: Accepts ``person`` (str) and ``language`` (str).

        Returns:
            str: Past-tense conjugated verb, e.g. "sued".
        """
        language = kwargs.get('language', None)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if self.number() > 1:
            if person in ('2', '2p'):
                tense = '2ppl'
            elif person in ('1', '1p'):
                tense = '1ppl'
            else:
                tense = '3ppl'
        else:
            if person == '2':
                tense = '2sgp'
            elif person == '2p':
                tense = '2ppl'
            elif person == '1':
                tense = '1sgp'
            elif person == '1p':
                tense = '1ppl'
            else:
                tense = '3sgp'
        return verb_past(the_verb, tense, language=language)

    def as_singular_noun(self):
        """Return the singular noun form derived from the set's instance name.

        E.g., ``player.as_singular_noun()`` returns ``"player"`` regardless
        of how many players are in the set.

        Returns:
            str: Singular noun form of the trailing part of the instance name.
        """
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun

    def quantity_noun(self, *pargs, **kwargs):
        """Return a noun phrase combining the number of items with the noun.

        Args:
            *pargs: Passed to the ``quantity_noun()`` function after the count.
            **kwargs: Passed through to ``quantity_noun()``.

        Returns:
            str: Phrase such as "3 players".
        """
        the_args = [self.number()] + list(pargs)
        return quantity_noun(*the_args, **kwargs)

    def as_noun(self, *pargs, **kwargs):
        """Return a singular or plural noun form for the set, derived from the instance name.

        E.g., ``player.as_noun()`` returns ``"player"`` or ``"players"``
        depending on how many items are in the set.

        Args:
            *pargs: If provided, the first argument overrides the noun instead
                of using the instance name.
            **kwargs: Accepts ``plural`` (bool), ``singular`` (bool),
                ``article`` (bool), ``some`` (bool), ``this`` (bool),
                ``capitalize`` (bool), and ``language`` (str).

        Returns:
            str: Noun form with optional article.
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
        """Return the number of items in the set, triggering gathering if needed.

        Returns:
            int: Count of items in the set.
        """
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return len(self.elements)

    def gathering_started(self):
        """Return True if any items have been gathered or ``there_are_any`` has been set.

        Returns:
            bool: True if gathering has started; False otherwise.
        """
        if hasattr(self, 'gathered') or hasattr(self, 'there_are_any') or len(self.elements) > 0:
            return True
        return False

    def number_gathered(self, if_started=False):
        """Return the count of items gathered so far, without triggering gathering.

        Args:
            if_started (bool): If True, trigger gathering when gathering has
                not yet started. Defaults to False.

        Returns:
            int: Number of items currently in the set.
        """
        if if_started and not self.gathering_started():
            self._trigger_gather()
        return len(self.elements)

    def number_as_word(self, language=None):
        """Return the number of items spelled out as a word when ten or fewer.

        Args:
            language (str, optional): Language code for localization.

        Returns:
            str: Spelled-out number (e.g., "three") for counts up to ten;
                numeral string otherwise.
        """
        return nice_number(self.number(), language=language)

    def gather(self, number=None, minimum=None):
        """Trigger the gathering process for the set and return True.

        Args:
            number (int, optional): Collect exactly this many items.
            minimum (int, optional): Minimum number of items to collect.

        Returns:
            bool: Always True once gathering is complete.
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
        """Return the set items as a comma-separated string with "and" before the last.

        Returns:
            str: Human-readable enumeration of items such as "Alice, Bob, and Carol".
        """
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
        """Return a new set that is the union of this set and another collection.

        Args:
            other_set: Any iterable or DASet to union with.

        Returns:
            DASet: Elements from either this set or ``other_set``.
        """
        self._trigger_gather()
        return self.__class__(elements=self.elements.union(setify(other_set)))

    def intersection(self, other_set):
        """Return a new set of elements present in both this set and another collection.

        Args:
            other_set: Any iterable or DASet to intersect with.

        Returns:
            DASet: Elements that appear in both this set and ``other_set``.
        """
        self._trigger_gather()
        return self.__class__(elements=self.elements.intersection(setify(other_set)))

    def difference(self, other_set):
        """Return a new set of elements in this set that are not in another collection.

        Args:
            other_set: Any iterable or DASet to subtract.

        Returns:
            DASet: Elements in this set but not in ``other_set``.
        """
        self._trigger_gather()
        return self.__class__(elements=self.elements.difference(setify(other_set)))

    def isdisjoint(self, other_set):
        """Return True if this set and another collection share no elements.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if there is no overlap; False otherwise.
        """
        self._trigger_gather()
        return self.elements.isdisjoint(setify(other_set))

    def issubset(self, other_set):
        """Return True if every element of this set is also in another collection.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if this set is a subset of ``other_set``; False
                otherwise.
        """
        self._trigger_gather()
        return self.elements.issubset(setify(other_set))

    def issuperset(self, other_set):
        """Return True if every element of another collection is in this set.

        Args:
            other_set: Any iterable or DASet to compare against.

        Returns:
            bool: True if ``other_set`` is a subset of this set; False
                otherwise.
        """
        self._trigger_gather()
        return self.elements.issuperset(setify(other_set))

    def pronoun_possessive(self, target, **kwargs):
        """Return a possessive pronoun phrase for the collection followed by the target.

        Args:
            target (str): The possessed noun phrase (e.g., ``"fish"``).
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: Possessive phrase such as "their fish".
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = your(target, **kwargs)
        elif person == '2p':
            output = docassemble.base.functions.your_plural(target, **kwargs)
        elif person == '1':
            output = docassemble.base.functions.my_possessive(target, **kwargs)
        elif person == '1p':
            output = docassemble.base.functions.our_possessive(target, **kwargs)
        else:
            output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun(self, **kwargs):
        """Return an objective pronoun appropriate for the set.

        Returns "them" for multiple items, or delegates to the single
        item for a one-item set.

        Args:
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: A pronoun such as "them", "her", "him", "you", or "us".
        """
        if self.number() == 1:
            self._trigger_gather()
            if isinstance(list(self.elements)[0], DAObject):
                return list(self.elements)[0].pronoun(**kwargs)
            return docassemble.base.functions.it_objective(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            output = docassemble.base.functions.you_objective_plural(**kwargs)
        elif person in ('1', '1p'):
            output = docassemble.base.functions.us_objective(**kwargs)
        else:
            output = docassemble.base.functions.them_objective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

    def pronoun_subjective(self, **kwargs):
        """Return a subjective pronoun appropriate for the collection.

        Returns "they" for multiple elements, or delegates to the single
        element for a one-item collection.

        Args:
            **kwargs: Accepts ``person`` (str) and ``capitalize`` (bool).

        Returns:
            str: A pronoun such as "they", "she", "he", "you", or "we".
        """
        if self.number() == 1:
            self._trigger_gather()
            if isinstance(list(self.elements)[0], DAObject):
                return list(self.elements)[0].pronoun_subjective(**kwargs)
            return docassemble.base.functions.it_subjective(**kwargs)
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person in ('2', '2p'):
            output = docassemble.base.functions.you_subjective_plural(**kwargs)
        elif person in ('1', '1p'):
            output = docassemble.base.functions.we_subjective(**kwargs)
        else:
            output = docassemble.base.functions.they_subjective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def hook_on_gather(self, *pargs, **kwargs):
        """Override this method to run code just before the set is marked as gathered."""

    def hook_after_gather(self, *pargs, **kwargs):
        """Override this method to run code just after the set is marked as gathered."""

    def hook_on_item_complete(self, item, *pargs, **kwargs):
        """Override this method to run code when an item becomes complete.

        Args:
            item: The item that has just been marked complete.
        """

    def hook_on_remove(self, item, *pargs, **kwargs):
        """Override this method to run code when an item is removed from the set.

        Args:
            item: The item being removed.
        """

    def __eq__(self, other):
        self._trigger_gather()
        return self.elements == other


class DAFile(DAObject):
    """Represent an uploaded, generated, or stored file in a docassemble interview.

    DAFile objects track a file by a server-side number and offer methods to
    read, write, convert, and display the file.

    Attributes:
        number (int): Internal file number used to locate the file on the
            server.
        ok (bool): True when the file has been initialized with a valid
            number.
        filename (str): Original or assigned filename, including extension.
        extension (str): Lowercase file extension (e.g., ``'pdf'``, ``'docx'``).
        mimetype (str): MIME type of the file.
        initialized (bool): True after the file storage slot has been created.
        alt_text (str): Alternative text for image display.
    """

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
        """Convert this file to a different format.

        Args:
            output_extension (str): Target file extension (e.g., ``'pdf'``).
            output_to (DAFile or DAFileList, optional): Destination file
                object. Defaults to converting this file in-place.

        Raises:
            DAError: If the file type cannot be identified or the conversion
                is not supported.
        """
        if output_to is None:
            output_to = self
        elif isinstance(output_to, DAFileList):
            output_to = output_to.elements[0]
        if not isinstance(output_to, DAFile):
            raise DAError("convert_to: output_to must be a DAFile")
        self.retrieve()
        if hasattr(self, 'extension'):
            input_extension = self.extension
        elif hasattr(self, 'filename'):
            input_extension, input_mimetype = server.get_ext_and_mimetype(self.filename)  # pylint: disable=assignment-from-none,unpacking-non-sequence,unused-variable
        else:
            raise DAError("DAFile.convert: could not identify file type")
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
            if can_convert_word_to_markdown():
                result = docassemble.base.pandoc.word_to_markdown(input_path, input_extension)
            else:
                result = None
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
            raise DAError("DAFile.convert: could not identify file type")
        output_to.commit()
        output_to.retrieve()

    def fix_up(self):
        """Attempt to repair the file in-place if it is corrupt or malformed.

        Raises:
            Exception: If the file is corrupt and cannot be repaired.
        """
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
        """Set the alternative text for the file (used in image display).

        Args:
            alt_text (str): The alt text to associate with this file.
        """
        self.alt_text = alt_text

    def get_alt_text(self):
        """Return the alternative text for the file, or None if not set.

        Returns:
            str or None: The alt text string, or None if not defined.
        """
        if hasattr(self, 'alt_text'):
            return str(self.alt_text)
        return None

    def set_mimetype(self, mimetype):
        """Set the MIME type of the file and update the extension accordingly.

        Args:
            mimetype (str): MIME type string (e.g., ``'image/jpeg'``).
        """
        self.mimetype = mimetype
        if mimetype == 'image/jpeg':
            self.extension = 'jpg'
        else:
            self.extension = re.sub(r'^\.', '', mimetypes.guess_extension(mimetype))

    def __str__(self):
        return str(self.show())

    def initialize(self, **kwargs):
        """Create the file on the server if it does not already exist and prepare it for use.

        Args:
            **kwargs: Accepts ``filename`` (str), ``mimetype`` (str),
                ``extension`` (str), ``content`` (str), ``markdown`` (str),
                ``alt_text`` (str), ``number`` (int), and
                ``reinitialize`` (bool). Pass ``reinitialize=True`` to delete
                the existing file and create a fresh one.
        """
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
        if hasattr(self, 'extension'):
            self.extension = server.secure_filename(self.extension)
        if not hasattr(self, 'filename'):
            if hasattr(self, 'extension'):
                self.filename = kwargs.get('filename', 'file.' + self.extension)
            else:
                self.filename = kwargs.get('filename', 'file.txt')
        self.filename = server.secure_filename_unicode_ok(self.filename)
        if self.filename == '':
            if hasattr(self, 'extension'):
                self.filename = 'file.' + self.extension
            else:
                self.filename = 'file.txt'
        if hasattr(self, 'number'):
            should_not_exist = False
        else:
            yaml_filename = None
            uid = None
            if hasattr(docassemble.base.functions.this_thread, 'current_info'):
                yaml_filename = docassemble.base.functions.this_thread.current_info.get('yaml_filename', None)
            uid = docassemble.base.functions.get_uid()
            self.number = server.get_new_file_number(uid, server.secure_filename_spaces_ok(self.filename) or 'file.txt', yaml_file_name=yaml_filename)  # pylint: disable=assignment-from-none
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
        """Ensure the file is available locally and update ``file_info``.

        Raises:
            DAError: If the file cannot be retrieved.
        """
        if not self.ok:
            self.initialize()
        if not hasattr(self, 'number'):
            raise DAError("Cannot retrieve a file without a file number.")
        docassemble.base.functions.this_thread.open_files.add(self)
        # logmessage("Retrieve: calling file finder")
        if self.has_specific_filename:
            self.file_info = server.file_number_finder(self.number, filename=self.filename)
        else:
            self.file_info = server.file_number_finder(self.number)
        if self.file_info is None:
            raise DAError("Could not retrieve file " + str(self.number))
        if 'path' not in self.file_info:
            raise DAError("Could not retrieve file: " + repr(self.file_info))
        self.extension = self.file_info.get('extension', None)
        self.mimetype = self.file_info.get('mimetype', None)
        self.persistent = self.file_info['persistent']
        self.private = self.file_info['private']

    def size_in_bytes(self):
        """Return the size of the file in bytes.

        Returns:
            int: Number of bytes in the file.
        """
        self.retrieve()
        the_path = self.path()
        return os.path.getsize(the_path)

    def slurp(self, auto_decode=True):
        """Return the entire contents of the file as a string or bytes.

        Args:
            auto_decode (bool): If True (the default), return a ``str`` for
                text and JSON files; otherwise return ``bytes``.

        Returns:
            str or bytes: File contents.

        Raises:
            DAError: If the file does not yet exist on disk.
        """
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise DAError("File " + str(the_path) + " does not exist yet.")
        if auto_decode and hasattr(self, 'mimetype') and (self.mimetype.startswith('text') or self.mimetype in ('application/json', 'application/javascript')):
            with open(the_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            with open(the_path, 'rb') as f:
                return f.read()

    def readlines(self):
        """Return the lines of the file as a list of strings.

        Returns:
            list[str]: Lines of the file including newline characters.

        Raises:
            DAError: If the file does not yet exist on disk.
        """
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise DAError("File does not exist yet.")
        with open(the_path, 'r', encoding='utf-8') as f:
            return f.readlines()

    def write(self, content, binary=False):
        """Write content to the file, replacing any existing contents.

        Args:
            content (str or bytes): The content to write.
            binary (bool): If True, open the file in binary mode for writing
                bytes. Defaults to False.
        """
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
        """Replace this file's contents with the contents of another file.

        Args:
            other_file (DAFile, DAFileList, DAFileCollection, DAStaticFile,
                or str): Source file object or filesystem path.
        """
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
            raise DAError("extract_pages: first must be an integer")
        if first < 1:
            raise DAError("extract_pages: first must be 1 or greater")
        if last is None:
            last = ''
        elif not isinstance(last, int):
            raise DAError("extract_pages: last must be an integer")
        elif last < first:
            raise DAError("extract_pages: last must greater than or equal to first")
        self.retrieve()
        if output_to is None:
            output_to = DAFile()
            output_to.set_random_instance_name()
        elif isinstance(output_to, DAFileList):
            output_to = output_to.elements[0]
        else:
            raise DAError("extract_pages: output_to must be a DAFile")
        input_filename = self.filename
        input_path = self.path()
        if output_to is self:
            temp_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".pdf", delete=False)
            shutil.copyfile(input_path, temp_file.name)
            input_path = temp_file.name
        output_to.initialize(extension='pdf', filename=input_filename, reinitialize=output_to.ok)
        try:
            docassemble.base.pdftk.extract_pages(input_path, output_to.path(), first, last)
        except BaseException as err:
            raise DAError("extract_pages: " + str(err))
        output_to.retrieve()
        output_to.commit()
        return output_to

    def bates_number(self, *pargs, **kwargs):
        """Apply Bates numbering to this file or a set of provided files.

        Args:
            *pargs: Optional source files (DAFile, DAFileList, DAFileCollection,
                or DAStaticFile) to Bates-number. If none provided, this file
                is used.
            **kwargs: Accepts ``filename`` (str), ``prefix`` (str, default
                ``'TEST'``), ``digits`` (int, default 5), ``start`` (int,
                default 1), ``area`` (str, one of ``'TOP_LEFT'``,
                ``'TOP_RIGHT'``, ``'BOTTOM_RIGHT'``, ``'BOTTOM_LEFT'``),
                ``font_size`` (int, default 10),
                ``offset_horizontal`` (int), ``offset_vertical`` (int).

        Raises:
            DAError: If Bates numbering fails.
        """
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
        prefix = kwargs.get('prefix') or 'TEST'
        digits = kwargs.get('digits') or 5
        start = kwargs.get('start') or 1
        area = kwargs.get('area') or None
        font_size = kwargs.get('font_size') or 10
        offset_horizontal = kwargs.get('offset_horizontal') or 15
        offset_vertical = kwargs.get('offset_vertical') or 15
        if area is None:
            area = 'BOTTOM_RIGHT'
        if area not in ('TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_RIGHT', 'BOTTOM_LEFT'):
            raise DAError("bates_number: area must be one of TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, or BOTTOM_LEFT")
        if filename is None:
            filename = 'file.pdf'
        args = [os.path.join(server.daconfig['modules'], 'bin', 'python'), '-m', 'docassemble.base.bates', '--prefix', str(prefix), '--digits', str(digits), '--start', str(start), '--area', area, '--font-size', str(font_size), '--offset-horizontal', str(offset_horizontal), '--offset-vertical', str(offset_vertical)]
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
        """Replace this file's contents with an OCR'd PDF of this or other files.

        Args:
            *pargs: Optional source files to OCR. Defaults to this file.
            **kwargs: Accepts ``language`` (str), ``psm`` (int), and
                ``preserve_color`` (bool).
        """
        lang = get_ocr_language(kwargs.get('language', None))
        ocr_pdf(*pargs, target=self, filename=kwargs.get('filename', None), lang=lang, psm=kwargs.get('psm', None), preserve_color=kwargs.get('preserve_color', False))

    def make_ocr_pdf_in_background(self, *pargs, **kwargs):
        """Asynchronously replace this file's contents with an OCR'd PDF.

        Starts a background Celery task. The result is a chord handle.

        Args:
            *pargs: Optional source files to OCR. Defaults to this file.
            **kwargs: Accepts ``language`` (str), ``psm`` (int),
                ``preserve_color`` (bool), ``dafilelist`` (DAFileList), and
                ``filename`` (str).

        Returns:
            AsyncResult: A Celery chord handle for the background task.
        """
        lang = get_ocr_language(kwargs.get('language', None))
        args = {'yaml_filename': docassemble.base.functions.this_thread.current_info['yaml_filename'], 'user': docassemble.base.functions.this_thread.current_info['user'], 'user_code': docassemble.base.functions.this_thread.current_info['session'], 'secret': docassemble.base.functions.this_thread.current_info['secret'], 'url': docassemble.base.functions.this_thread.current_info['url'], 'url_root': docassemble.base.functions.this_thread.current_info['url_root'], 'language': lang, 'psm': kwargs.get('psm', None), 'x': None, 'y': None, 'W': None, 'H': None, 'extra': None, 'message': None, 'pdf': True, 'preserve_color': kwargs.get('preserve_color', False), 'target': self, 'dafilelist': kwargs.get('dafilelist', None), 'filename': kwargs.get('filename', None)}
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
        """Return a list of Jinja2 variable names used in a DOCX template file.

        Returns:
            list[str]: Variable names referenced in the document template.
        """
        return docassemble.base.parse.get_docx_variables(self.path())

    def get_pdf_fields(self):
        """Return a list of form fields found in the PDF document.

        Returns:
            list[tuple]: Each tuple contains field information: name, value,
                position, page number, field type, and flags.
        """
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
        """Download content from a URL and store it as this file's contents.

        Args:
            url (str): The URL to download.
        """
        self.retrieve()
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(self.file_info['path'], 'wb') as fp:
                    for chunk in r.iter_content(8192):
                        fp.write(chunk)
        except requests.exceptions.HTTPError as err:
            raise DAError("from_url: Error %s" % (str(err),))
        self.retrieve()

    def uses_acroform(self):
        """Return True if the PDF file uses AcroForm fields.

        Returns:
            bool: True if the file uses AcroForm; False otherwise.
        """
        if not hasattr(self, 'file_info'):
            self.retrieve()
        return self.file_info.get('acroform', False)

    def is_encrypted(self):
        """Return True if the file is an encrypted PDF.

        Returns:
            bool: True if the file is an encrypted PDF; False otherwise.
        """
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
        """Return True if the PNG page images for the PDF have been generated.

        Returns:
            bool: True if all PNG images are ready; False otherwise.
        """
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
        """Return the number of pages in the file.

        Returns:
            int: Number of pages for a PDF; 1 for all other file types.

        Raises:
            DAError: If the file has no file number assigned.
        """
        if not self.ok:
            self.initialized  # pylint: disable=pointless-statement
        if not hasattr(self, 'number'):
            raise DAError("Cannot get pages in file without a file number.")
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
            raise DAError("Cannot get path of file without a file number.")
        self.retrieve()
        if 'fullpath' not in self.file_info:
            raise DAError("fullpath not found.")
        return self.file_info['path'] + 'page' + str(page) + '.pdf'

    def _path_ready(self, the_path):
        if os.path.isfile(the_path):
            if time.time() - os.stat(the_path)[stat.ST_MTIME] < 3:
                time.sleep(1)
            return True
        return False

    def page_path(self, page, prefix, wait=True):
        """Return the filesystem path for a PDF page image.

        Args:
            page (int): One-based page number.
            prefix (str): Image type prefix, either ``'page'`` or ``'screen'``.
            wait (bool): If True, wait for the image to be generated if not
                yet ready. Defaults to True.

        Returns:
            str or None: Filesystem path to the PNG image, or None if not
                ready and ``wait`` is False.

        Raises:
            DAError: If the file has no number or page count information.
        """
        if not self.ok:
            self.initialized  # pylint: disable=pointless-statement
        if not hasattr(self, 'number'):
            raise DAError("Cannot get path of file without a file number.")
        self.retrieve()
        if 'fullpath' not in self.file_info:
            raise DAError("fullpath not found.")
        if 'pages' not in self.file_info:
            raise DAError("number of pages not found. " + repr(self.file_info))
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
        """Return the cloud storage path for the file, or None if cloud storage is not enabled.

        Args:
            filename (str, optional): Specific filename within the file's
                cloud storage directory.

        Returns:
            str or None: Cloud storage path (S3 or Azure Blob), or None.

        Raises:
            DAError: If the file has no file number assigned.
        """
        if not self.ok and not hasattr(self, 'content'):
            self.initialized  # pylint: disable=pointless-statement
        if not hasattr(self, 'number'):
            raise DAError("Cannot get the cloud path of file without a file number.")
        return server.SavedFile(self.number, fix=False).cloud_path(filename)

    def path(self):
        """Return the filesystem path at which the file can be accessed.

        Returns:
            str: Absolute filesystem path to the file.

        Raises:
            DAError: If the file has no file number assigned or the path
                cannot be determined.
        """
        # logmessage("path")
        if not self.ok and not hasattr(self, 'content'):
            self.initialized  # pylint: disable=pointless-statement
        if not hasattr(self, 'number'):
            raise DAError("Cannot get path of file without a file number.")
        # if not hasattr(self, 'file_info'):
        self.retrieve()
        if 'fullpath' not in self.file_info:
            raise DAError("fullpath not found.")
        return self.file_info['fullpath']

    def commit(self):
        """Persist any changes to the file so they are available in the future."""
        if hasattr(self, 'number'):
            sf = server.SavedFile(self.number, fix=True)
            sf.finalize()

    def show(self, width=None, wait=True, alt_text=None):
        """Return markup that displays the file inline.

        Args:
            width (str or int, optional): Display width for images.
            wait (bool): If True, wait for PDF page images to be generated
                before returning markup. Defaults to True.
            alt_text (str, optional): Alternative text for the image.

        Returns:
            str: Markup string for embedding the file in interview output.
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
        if alt_text is None:
            alt_text = self.get_alt_text()
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            if self.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return docassemble.base.file_docx.include_docx_template(self, _use_jinja2=False)
            if self.mimetype in ('application/pdf', 'application/rtf', 'application/vnd.oasis.opendocument.text', 'application/msword'):
                return self._pdf_pages(width)
            return docassemble.base.file_docx.image_for_docx(self.number, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width, alt_text=alt_text)
        if width is not None:
            the_width = str(width)
        else:
            the_width = 'None'
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
        """Return a URL at which the file can be accessed.

        Args:
            **kwargs: Accepts ``temporary`` (bool), ``external`` (bool), and
                ``attachment`` (bool).

        Returns:
            str: URL string for the file.
        """
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
        """Set server-side attributes for the file.

        Args:
            **kwargs: Accepts ``private`` (bool), ``persistent`` (bool), and
                ``filename`` (str).
        """
        if 'private' in kwargs and kwargs['private'] in [True, False]:
            self.private = kwargs['private']
        if 'persistent' in kwargs and kwargs['persistent'] in [True, False]:
            self.persistent = kwargs['persistent']
        if 'filename' in kwargs:
            self.filename = server.secure_filename_unicode_ok(kwargs['filename'])
            if kwargs['filename'] == '':
                if hasattr(self, 'extension'):
                    self.extension = server.secure_filename(self.extension)
                    self.filename = 'file.' + self.extension
                else:
                    self.filename = 'file.txt'
                kwargs['filename'] = server.secure_filename_spaces_ok(self.filename)
        if 'session' in kwargs:
            del kwargs['session']
        return server.file_set_attributes(self.number, **kwargs)

    def user_access(self, *pargs, **kwargs):
        """Grant or revoke access to the file for specific users.

        Args:
            *pargs: User objects whose access should be modified.
            **kwargs: Accepts ``allow`` (bool, default True) and ``access``
                (str) to specify access level.
        """
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
        """Grant or revoke access to the file for users with specific privileges.

        Args:
            *pargs (str): Privilege names to grant access.
            **kwargs: Accepts ``disallow`` (str, list, or ``'all'``) to
                revoke access from named privileges or all privileges.
        """
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
    """Represent a collection of DAFile objects for the same document in multiple formats.

    Created by the ``attachments`` feature to group a document's PDF, DOCX,
    and RTF renderings. Each format is accessible as an attribute (e.g.,
    ``collection.pdf``, ``collection.docx``).

    Attributes:
        pdf (DAFile): The PDF version of the document, if available.
        docx (DAFile): The DOCX version of the document, if available.
        rtf (DAFile): The RTF version of the document, if available.
    """

    def init(self, *pargs, **kwargs):
        self.info = {}
        super().init(*pargs, **kwargs)

    def _extension_list(self):
        if hasattr(self, 'info') and 'formats' in self.info:
            return [item for item in self.info['formats'] if item != 'html']
        return ['pdf', 'docx', 'rtf']

    def fix_up(self):
        """Attempt to repair each file in the collection in-place.

        Raises:
            Exception: If a file is corrupt and cannot be repaired.
        """
        for ext in self._extension_list():
            if hasattr(self, ext):
                getattr(self, ext).fix_up()

    def set_alt_text(self, alt_text):
        """Set the alternative text on each file in the collection.

        Args:
            alt_text (str): The alt text to set on all files.
        """
        for ext in self._extension_list():
            if hasattr(self, ext):
                getattr(self, ext).alt_text = alt_text

    def get_alt_text(self):
        """Return the alternative text of the first file in the collection, or None.

        Returns:
            str or None: Alt text of the first file, or None if not defined.
        """
        for ext in self._extension_list():
            if hasattr(self, ext):
                return getattr(self, ext).get_alt_text()
        return None

    def uses_acroform(self):
        """Return True if the collection has a PDF file that uses AcroForm.

        Returns:
            bool: True if the PDF uses AcroForm; False otherwise.
        """
        if hasattr(self, 'pdf'):
            return self.pdf.uses_acroform()
        return False

    def is_encrypted(self):
        """Return True if the collection has an encrypted PDF file.

        Returns:
            bool: True if the PDF is encrypted; False otherwise.
        """
        if hasattr(self, 'pdf'):
            return self.pdf.is_encrypted()
        return False

    def num_pages(self):
        """Return the page count of the PDF file in the collection, or 1 if none.

        Returns:
            int: Number of pages in the PDF, or 1 if no PDF is present.
        """
        if hasattr(self, 'pdf'):
            return self.pdf.num_pages()
        return 1

    def _first_file(self):
        for ext in self._extension_list():
            if hasattr(self, ext):
                return getattr(self, ext)
        return None

    def path(self):
        """Return the filesystem path of the first available file in the collection.

        Returns:
            str or None: Absolute path to the first available file, or None.
        """
        the_file = self._first_file()
        if the_file is None:
            return None
        return the_file.path()

    def get_docx_variables(self):
        """Return a list of Jinja2 variable names used in a DOCX template file.

        Returns:
            list[str]: Variable names referenced in the document template.
        """
        if hasattr(self, 'docx'):
            return self.docx.get_docx_variables()
        return None

    def get_pdf_fields(self):
        """Return a list of form fields found in the PDF document.

        Returns:
            list[tuple]: Each tuple contains field information: name, value,
                position, page number, field type, and flags.
        """
        if hasattr(self, 'pdf'):
            return self.pdf.get_pdf_fields()
        return None

    def url_for(self, **kwargs):
        """Return a URL to the first available file in the collection.

        Args:
            **kwargs: Passed through to the individual file's ``url_for()``.

        Returns:
            str: URL for the first available format.

        Raises:
            DAError: If no file is found in the collection.
        """
        for ext in self._extension_list():
            if hasattr(self, ext):
                return getattr(self, ext).url_for(**kwargs)
        raise DAError("Could not find a file within a DACollection.")

    def set_attributes(self, **kwargs):
        """Set server-side attributes on each file in the collection.

        Args:
            **kwargs: Accepts ``private`` (bool) and ``persistent`` (bool).
                The ``filename`` argument is ignored.
        """
        if 'filename' in kwargs:
            del kwargs['filename']
        for ext in self._extension_list():
            if hasattr(self, ext):
                getattr(self, ext).set_attributes(**kwargs)

    def user_access(self, *pargs, **kwargs):
        """Grant or revoke access to all files in the collection for specific users.

        Args:
            *pargs: User objects whose access should be modified.
            **kwargs: Passed through to each file's ``user_access()``.
        """
        for ext in self._extension_list():
            if hasattr(self, ext):
                if getattr(self, ext).ok:
                    getattr(self, ext).user_access(*pargs, **kwargs)

    def privilege_access(self, *pargs, **kwargs):
        """Grant or revoke access to all files in the collection for specific privileges.

        Args:
            *pargs (str): Privilege names to grant access.
            **kwargs: Passed through to each file's ``privilege_access()``.
        """
        for ext in self._extension_list():
            if hasattr(self, ext):
                if getattr(self, ext).ok:
                    getattr(self, ext).privilege_access(*pargs, **kwargs)

    def show(self, **kwargs):
        """Return markup that displays each file in the collection inline.

        Returns:
            str: Markup for embedding the collection files in interview output.
        """
        the_files = [getattr(self, ext).show(**kwargs) for ext in self._extension_list() if hasattr(self, ext)]
        for the_file in the_files:
            if isinstance(the_file, (InlineImage, Subdoc)):
                return the_file
        return ' '.join(the_files)

    def extract_pages(self, first=None, last=None):
        """Extract a page range from the PDF and return a new DAFile.

        Args:
            first (int, optional): First page to include (1-based). Defaults
                to 1.
            last (int, optional): Last page to include (inclusive). Defaults
                to the last page.

        Returns:
            DAFile: A new DAFile containing the extracted pages.

        Raises:
            DAError: If no PDF is available.
        """
        if not hasattr(self, 'pdf'):
            raise DAError("Cannot call extract_pages() on a DAFileCollection object without a pdf attribute.")
        return self.pdf.extract_pages(first=first, last=last)

    def bates_number(self, **kwargs):
        """Apply Bates numbering to the collection's PDF file in-place.

        Args:
            **kwargs: Passed through to the PDF file's ``bates_number()``.

        Raises:
            DAError: If the collection has no PDF attribute.
        """
        if not hasattr(self, 'pdf'):
            raise DAError("Cannot call bates_number() on a DAFileCollection object without a pdf attribute.")
        self.pdf.bates_number(**kwargs)

    def make_ocr_pdf(self, **kwargs):
        """Replace the collection's PDF file with an OCR'd version.

        Args:
            **kwargs: Passed through to the PDF file's ``make_ocr_pdf()``.

        Raises:
            DAError: If the collection has no PDF attribute.
        """
        if not hasattr(self, 'pdf'):
            raise DAError("Cannot call make_ocr_pdf() on a DAFileCollection object without a pdf attribute.")
        self.pdf.make_ocr_pdf(**kwargs)

    def make_ocr_pdf_in_background(self, **kwargs):
        """Asynchronously replace the collection's PDF with an OCR'd version.

        Args:
            **kwargs: Passed through to the PDF file's
                ``make_ocr_pdf_in_background()``.

        Returns:
            AsyncResult: A Celery chord handle for the background task.

        Raises:
            DAError: If the collection has no PDF attribute.
        """
        if not hasattr(self, 'pdf'):
            raise DAError("Cannot call make_ocr_pdf_in_background() on a DAFileCollection object without a pdf attribute.")
        return self.pdf.make_ocr_pdf_in_background(**kwargs)

    def __str__(self):
        return str(self._first_file())


class DAFileList(DAList):
    """A list of DAFile objects, typically from a multi-file upload field.

    Inherits from DAList and is used internally to manage uploaded files.
    Each element is a DAFile. Most file operations (e.g., ``path()``,
    ``url_for()``, ``show()``) delegate to the first element.
    """

    def init(self, *pargs, **kwargs):
        if 'complete_attribute' not in kwargs:
            kwargs['complete_attribute'] = 'initialized'
        if 'object_type' not in kwargs:
            kwargs['object_type'] = DAFile
        super().init(*pargs, **kwargs)

    def __str__(self):
        return str(self.show())

    def fix_up(self):
        """Attempt to repair each file in the list in-place.

        Raises:
            Exception: If a file is corrupt and cannot be repaired.
        """
        for item in self.elements:
            item.fix_up()

    def set_alt_text(self, alt_text):
        """Set the alternative text on each file in the list.

        Args:
            alt_text (str): The alt text to assign to all files.
        """
        for item in self:
            item.alt_text = alt_text

    def get_alt_text(self):
        """Return the alternative text of the first file in the list, or None.

        Returns:
            str or None: Alt text of the first file, or None if the list is
                empty or no alt text is defined.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].get_alt_text()

    def num_pages(self):
        """Return the total page count across all files in the list.

        Returns:
            int: Sum of pages for PDF files; non-PDF files count as one page
                each.
        """
        result = 0
        for element in sorted(self.elements):
            if element.ok:
                result += element.num_pages()
        return result

    def uses_acroform(self):
        """Return True if the first file is a PDF that uses AcroForm.

        Returns:
            bool or None: True if the first file uses AcroForm; None if the
                list is empty.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].uses_acroform()

    def is_encrypted(self):
        """Return True if the first file is an encrypted PDF.

        Returns:
            bool or None: True if the first file is an encrypted PDF; None
                if the list is empty.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].is_encrypted()

    def convert_to(self, output_extension, output_to=None):
        """Convert each file in the list to a different format.

        Args:
            output_extension (str): Target file extension (e.g., ``'pdf'``).
            output_to (DAFile or DAFileList, optional): Destination file;
                converts in-place when None.
        """
        for element in self.elements:
            element.convert_to(output_extension, output_to=output_to)

    def size_in_bytes(self):
        """Return the size in bytes of the first file, or None if the list is empty.

        Returns:
            int or None: Byte count of the first file, or None.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].size_in_bytes()

    def slurp(self, auto_decode=True):
        """Return the contents of the first file, or None if the list is empty.

        Args:
            auto_decode (bool): If True (the default), return ``str`` for
                text files; otherwise return ``bytes``.

        Returns:
            str, bytes, or None: File contents, or None if the list is empty.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].slurp(auto_decode=auto_decode)

    def show(self, width=None, alt_text=None):
        """Return markup that displays each file in the list inline.

        Args:
            width (str or int, optional): Display width for images.
            alt_text (str, optional): Alternative text for images.

        Returns:
            str: Markup for embedding the files in interview output.
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
        """Return the filesystem path of the first file in the list.

        Returns:
            str or None: Path to the first file, or None if the list is empty.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].path()

    def get_docx_variables(self):
        """Return a list of Jinja2 variable names used in a DOCX template file.

        Returns:
            list[str]: Variable names referenced in the document template.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].get_docx_variables()

    def get_pdf_fields(self):
        """Return a list of form fields found in the PDF document.

        Returns:
            list[tuple]: Each tuple contains field information: name, value,
                position, page number, field type, and flags.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].get_pdf_fields()

    def url_for(self, **kwargs):
        """Return a URL for the first file in the list.

        Args:
            **kwargs: Passed through to the first file's ``url_for()``.

        Returns:
            str or None: URL for the first file, or None if the list is empty.
        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].url_for(**kwargs)

    def set_attributes(self, **kwargs):
        """Set server-side attributes on each file in the list.

        Args:
            **kwargs: Accepts ``private`` (bool) and ``persistent`` (bool).
                The ``filename`` argument is ignored.
        """
        if 'filename' in kwargs:
            del kwargs['filename']
        for element in sorted(self.elements):
            if element.ok:
                element.set_attributes(**kwargs)

    def user_access(self, *pargs, **kwargs):
        """Grant or revoke access to all files in the list for specific users.

        Args:
            *pargs: User objects whose access should be modified.
            **kwargs: Passed through to each file's ``user_access()``.
        """
        for element in sorted(self.elements):
            if element.ok:
                element.user_access(*pargs, **kwargs)

    def privilege_access(self, *pargs, **kwargs):
        """Grant or revoke access to all files in the list for specific privileges.

        Args:
            *pargs (str): Privilege names to grant access.
            **kwargs: Passed through to each file's ``privilege_access()``.
        """
        for element in sorted(self.elements):
            if element.ok:
                element.privilege_access(*pargs, **kwargs)

    def extract_pages(self, first=None, last=None):
        """Extract a page range from the PDF and return a new DAFile.

        Args:
            first (int, optional): First page to include (1-based). Defaults
                to 1.
            last (int, optional): Last page to include (inclusive). Defaults
                to the last page.

        Returns:
            DAFile: A new DAFile containing the extracted pages.

        Raises:
            DAError: If no PDF is available.
        """
        return self.elements[0].extract_pages(first=first, last=last)

    def bates_number(self, **kwargs):
        """Apply Bates numbering to the list of files and store the result in the first file.

        Args:
            **kwargs: Passed through to the first file's ``bates_number()``.
        """
        if len(self.elements) == 0:
            return
        if len(self.elements) > 1:
            self.elements[0].bates_number(self, **kwargs)
            self.elements = [self.elements[0]]
        else:
            self.elements[0].bates_number(self.elements[0], **kwargs)
        return

    def make_ocr_pdf(self, **kwargs):
        """OCR the list of files and store the result in the first file.

        Args:
            **kwargs: Passed through to the first file's ``make_ocr_pdf()``.
        """
        if len(self.elements) == 0:
            return
        if len(self.elements) > 1:
            self.elements[0].make_ocr_pdf(self, **kwargs)
            self.elements = [self.elements[0]]
        else:
            self.elements[0].make_ocr_pdf(**kwargs)

    def make_ocr_pdf_in_background(self, **kwargs):
        """Asynchronously OCR the list of files and store the result in the first file.

        Args:
            **kwargs: Passed through to the first file's
                ``make_ocr_pdf_in_background()``.

        Returns:
            AsyncResult or None: Celery chord handle, or None if the list is
                empty.
        """
        if len(self.elements) == 0:
            return None
        if len(self.elements) > 1:
            kwargs['dafilelist'] = self
            return self.elements[0].make_ocr_pdf_in_background(self, **kwargs)
        return self.elements[0].make_ocr_pdf_in_background(**kwargs)


class DAStaticFile(DAObject):
    """Represent a static file included with a docassemble package.

    Provides access to files in the ``data/static/`` directory of a package.
    Supports the same display and information methods as DAFile.

    Attributes:
        filename (str): The package-relative or fully qualified filename.
        package (str): The Python package that contains the file.
        extension (str): Lowercase file extension.
        mimetype (str): MIME type of the file.
        alt_text (str): Alternative text for image display.
    """

    def init(self, *pargs, **kwargs):
        if 'filename' in kwargs and 'mimetype' not in kwargs and 'extension' not in kwargs:
            self.extension, self.mimetype = server.get_ext_and_mimetype(kwargs['filename'])  # pylint: disable=assignment-from-none,unpacking-non-sequence
        self.package = docassemble.base.functions.this_thread.current_question.package
        super().init(*pargs, **kwargs)

    def _populate(self):
        if not hasattr(self, 'extension') or not hasattr(self, 'mimetype'):
            self.extension, self.mimetype = server.get_ext_and_mimetype(self.filename)  # pylint: disable=assignment-from-none,unpacking-non-sequence

    def get_alt_text(self):
        """Return the alternative text for the file, or None if not set.

        Returns:
            str or None: The alt text string, or None if not defined.
        """
        if hasattr(self, 'alt_text'):
            return str(self.alt_text)
        return None

    def set_alt_text(self, alt_text):
        """Set the alternative text for the file (used in image display).

        Args:
            alt_text (str): The alt text to associate with this file.
        """
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
        """Return markup that displays the static file inline.

        Args:
            width (str or int, optional): Display width for images.
            alt_text (str, optional): Alternative text for the image.

        Returns:
            str: Markup string for embedding the file in interview output.
        """
        self._populate()
        if alt_text is None:
            alt_text = self.get_alt_text()
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            if self.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return docassemble.base.file_docx.include_docx_template(self)
            if self.mimetype in ('application/pdf', 'application/rtf', 'application/vnd.oasis.opendocument.text', 'application/msword'):
                return self._pdf_pages(width)
            the_text = docassemble.base.file_docx.image_for_docx(docassemble.base.functions.DALocalFile(self.path()), docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width, alt_text=alt_text)
            return the_text
        if width is not None:
            the_width = str(width)
        else:
            the_width = 'None'
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
        """Return True if the static file is a PDF that uses AcroForm.

        Returns:
            bool: True if the file uses AcroForm; False otherwise.
        """
        file_info = server.file_finder(self._get_unqualified_reference())
        return file_info.get('acroform', False)

    def is_encrypted(self):
        """Return True if the file is an encrypted PDF.

        Returns:
            bool: True if the file is an encrypted PDF; False otherwise.
        """
        file_info = server.file_finder(self._get_unqualified_reference())
        return file_info.get('encrypted', False)

    def size_in_bytes(self):
        """Return the size of the file in bytes.

        Returns:
            int: Number of bytes in the file.
        """
        the_path = self.path()
        return os.path.getsize(the_path)

    def slurp(self, auto_decode=True):
        """Return the entire contents of the file as a string or bytes.

        Args:
            auto_decode (bool): If True (the default), return a ``str`` for
                text and JSON files; otherwise return ``bytes``.

        Returns:
            str or bytes: File contents.

        Raises:
            DAError: If the file does not yet exist on disk.
        """
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise DAError("File " + str(the_path) + " does not exist.")
        if auto_decode and hasattr(self, 'mimetype') and (self.mimetype.startswith('text') or self.mimetype in ('application/json', 'application/javascript')):
            with open(the_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            with open(the_path, 'rb') as f:
                return f.read()

    def path(self):
        """Return the filesystem path at which the static file can be accessed.

        Returns:
            str or None: Absolute filesystem path to the file, or None if not
                found.
        """
        file_info = server.file_finder(self._get_unqualified_reference())
        return file_info.get('fullpath', None)

    def get_docx_variables(self):
        """Return a list of Jinja2 variable names used in a DOCX template file.

        Returns:
            list[str]: Variable names referenced in the document template.
        """
        return docassemble.base.parse.get_docx_variables(self.path())

    def get_pdf_fields(self):
        """Return a list of form fields found in the PDF document.

        Returns:
            list[tuple]: Each tuple contains field information: name, value,
                position, page number, field type, and flags.
        """
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
        """Return a URL that points to the static file.

        Args:
            **kwargs: Optional keyword arguments. ``external=True`` generates
                an absolute URL; ``attachment=True`` sets the
                Content-Disposition header to trigger a download.

        Returns:
            str: URL to the static file.
        """
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
    """A list of DAEmailRecipient objects used to address an outgoing email."""

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
    """A single email recipient with a name and address.

    Attributes:
        name (str): Display name of the recipient.
        address (str): Email address of the recipient.
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
        """Return the recipient's email address, optionally including the display name.

        Args:
            include_name (bool or None): If True, include the name in RFC 5321
                format (``"Name" <address>``). If None (the default), include
                the name only when it is non-empty.

        Returns:
            str: Formatted email address string.
        """
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
    """An email message received through docassemble's email-receiving feature.

    Attributes:
        subject (str): Subject line of the received email.
        from_address (DAEmailRecipient): Sender of the email.
        to_address (DAEmailRecipientList): Primary recipients.
        cc_address (DAEmailRecipientList): Carbon-copy recipients.
        reply_to (DAEmailRecipient): Reply-to address, if present.
        body_text (str): Plain-text body of the email.
        body_html (str): HTML body of the email.
        attachments (DAFileList): Files attached to the email.
    """

    def __str__(self):
        return 'This is an e-mail'


class DATemplate(DAObject):
    """A Markdown template created from a ``template`` block.

    Attributes:
        subject (str): Subject line of the template (used for email subjects).
        content (str): Markdown body of the template.
        decorations (list): List of decoration identifiers attached to the
            template.
    """

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
        """Return the rendered content of the template as a string.

        Returns:
            str: Rendered template content.
        """
        return str(self)

    def show_as_markdown(self, **kwargs):  # pylint: disable=unused-argument
        """Return the raw Markdown content of the template.

        Returns:
            str: Markdown source of the template content.
        """
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
        the_elements = list(the_iterable.items())
        if table_info.filter_expression is not None:
            new_elements = []
            for indexno_item in the_elements:
                user_dict_copy['row_item'] = indexno_item[1]
                user_dict_copy['row_index'] = indexno_item[0]
                if eval(table_info.filter_expression, user_dict_copy):
                    new_elements.append(indexno_item)
            the_elements = new_elements
        if table_info.sort_key is not None:
            if 'operator' not in user_dict_copy:
                exec('import operator', user_dict_copy)
            if 'functools' not in user_dict_copy:
                exec('import functools', user_dict_copy)
            sort_key = eval(table_info.sort_key, user_dict_copy)
            sort_reverse = bool(eval(table_info.sort_reverse, user_dict_copy))
            the_elements = list(sorted(the_elements, key=sort_key, reverse=sort_reverse))
        elif not isinstance(the_iterable, (OrderedDict, DAOrderedDict)):
            the_elements = list(sorted(the_elements, key=lambda y: y[0]))
            if table_info.sort_reverse is not None and bool(eval(table_info.sort_reverse, user_dict_copy)):
                the_elements = list(reversed(the_elements))
        elif table_info.sort_reverse is not None and bool(eval(table_info.sort_reverse, user_dict_copy)):
            the_elements = list(reversed(the_elements))
        for indexno, item in the_elements:
            user_dict_copy['row_item'] = item
            user_dict_copy['row_index'] = indexno
            if table_info.show_incomplete:
                contents.append([table_safe_eval(x, user_dict_copy, table_info) for x in table_info.column])
            else:
                contents.append([table_safe(eval(x, user_dict_copy)) for x in table_info.column])
    else:
        the_elements = list(enumerate(the_iterable))
        if table_info.filter_expression is not None:
            new_elements = []
            for indexno_item in the_elements:
                user_dict_copy['row_item'] = indexno_item[1]
                user_dict_copy['row_index'] = indexno_item[0]
                if eval(table_info.filter_expression, user_dict_copy):
                    new_elements.append(indexno_item)
            the_elements = new_elements
        if table_info.sort_key is not None:
            if 'operator' not in user_dict_copy:
                exec('import operator', user_dict_copy)
            if 'functools' not in user_dict_copy:
                exec('import functools', user_dict_copy)
            sort_key = eval(table_info.sort_key, user_dict_copy)
            sort_reverse = bool(eval(table_info.sort_reverse, user_dict_copy))
            the_elements = list(sorted(the_elements, key=lambda y: sort_key(y[1]), reverse=sort_reverse))
        elif table_info.sort_reverse is not None and bool(eval(table_info.sort_reverse, user_dict_copy)):
            the_elements = list(reversed(the_elements))
        for indexno, item in the_elements:
            user_dict_copy['row_item'] = item
            user_dict_copy['row_index'] = indexno
            if table_info.show_incomplete:
                contents.append([table_safe_eval(x, user_dict_copy, table_info) for x in table_info.column])
            else:
                contents.append([table_safe(eval(x, user_dict_copy)) for x in table_info.column])
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
    def content(self):
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
            raise DAError("export: unsupported file format")
        header_output, contents = self.header_and_contents()
        import pandas  # pylint: disable=import-outside-toplevel
        df = pandas.DataFrame.from_records(contents, columns=header_output)
        if output_to is None:
            output_to = DAFile()
            output_to.set_random_instance_name()
        elif isinstance(output_to, DAFileList):
            output_to = output_to.elements[0]
        if not isinstance(output_to, DAFile):
            raise DAError("export: output_to must be a DAFile")
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
                                        engine_kwargs={'options': {'remove_timezone': True}})
            df.to_excel(writer, sheet_name=title, index=False, freeze_panes=freeze_panes)
            writer.close()
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
        import pandas  # pylint: disable=import-outside-toplevel
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
            the_elements = list(the_iterable.items())
            if self.table_info.filter_expression is not None:
                new_elements = []
                for indexno_item in the_elements:
                    user_dict_copy['row_item'] = indexno_item[1]
                    user_dict_copy['row_index'] = indexno_item[0]
                    if eval(self.table_info.filter_expression, user_dict_copy):
                        new_elements.append(indexno_item)
                the_elements = new_elements
            if self.table_info.sort_key is not None:
                if 'operator' not in user_dict_copy:
                    exec('import operator', user_dict_copy)
                if 'functools' not in user_dict_copy:
                    exec('import functools', user_dict_copy)
                sort_key = eval(self.table_info.sort_key, user_dict_copy)
                sort_reverse = bool(eval(self.table_info.sort_reverse, user_dict_copy))
                the_elements = list(sorted(the_elements, key=sort_key, reverse=sort_reverse))
            elif not isinstance(the_iterable, (OrderedDict, DAOrderedDict)):
                the_elements = list(sorted(the_elements, key=lambda y: y[0]))
                if self.table_info.sort_reverse is not None and bool(eval(self.table_info.sort_reverse, user_dict_copy)):
                    the_elements = list(reversed(the_elements))
            elif self.table_info.sort_reverse is not None and bool(eval(self.table_info.sort_reverse, user_dict_copy)):
                the_elements = list(reversed(the_elements))
            for indexno, item in the_elements:
                user_dict_copy['row_item'] = item
                user_dict_copy['row_index'] = indexno
                if self.table_info.show_incomplete:
                    contents.append([self.export_safe_eval(x, user_dict_copy) for x in self.table_info.column])
                else:
                    contents.append([export_safe(eval(x, user_dict_copy)) for x in self.table_info.column])
        else:
            the_elements = list(enumerate(the_iterable))
            if self.table_info.filter_expression is not None:
                new_elements = []
                for indexno_item in the_elements:
                    user_dict_copy['row_item'] = indexno_item[1]
                    user_dict_copy['row_index'] = indexno_item[0]
                    if eval(self.table_info.filter_expression, user_dict_copy):
                        new_elements.append(indexno_item)
                the_elements = new_elements
            if self.table_info.sort_key is not None:
                if 'operator' not in user_dict_copy:
                    exec('import operator', user_dict_copy)
                if 'functools' not in user_dict_copy:
                    exec('import functools', user_dict_copy)
                sort_key = eval(self.table_info.sort_key, user_dict_copy)
                sort_reverse = bool(eval(self.table_info.sort_reverse, user_dict_copy))
                the_elements = list(sorted(the_elements, key=lambda y: sort_key(y[1]), reverse=sort_reverse))
            elif self.table_info.sort_reverse is not None and bool(eval(self.table_info.sort_reverse, user_dict_copy)):
                the_elements = list(reversed(the_elements))
            for indexno, item in the_elements:
                user_dict_copy['row_item'] = item
                user_dict_copy['row_index'] = indexno
                if self.table_info.show_incomplete:
                    contents.append([export_safe(eval(x, user_dict_copy)) for x in self.table_info.column])
                else:
                    contents.append([self.export_safe_eval(x, user_dict_copy) for x in self.table_info.column])
        if self.table_info.is_editable:
            for cols in contents:
                cols.pop()
        user_dict_copy.pop('row_item', None)
        user_dict_copy.pop('row_index', None)
        return header_output, contents


def selections(*pargs, **kwargs):
    """Build a list of choice dictionaries from DAObject instances for use in a multiple-choice field.

    Args:
        *pargs: One or more DAObject instances, DAList/DASet collections, or
            plain lists containing DAObjects to include as choices.
        **kwargs: Optional keyword arguments:
            - ``object_labeler`` (callable): Function that returns the display
              label for each object. Defaults to ``str``.
            - ``help_generator`` (callable): Function that returns help text
              for each object, or None to omit help.
            - ``image_generator`` (callable): Function that returns an image
              reference for each object, or None to omit images.
            - ``exclude``: Object(s) to exclude from the choices.
            - ``default``: Object(s) to mark as selected by default.

    Returns:
        list[dict]: List of choice dictionaries suitable for use as ``code``
            in a ``choices`` field.
    """
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


def objects_from_data(data, recursive=True, gathered=True, name=None, package=None):
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
    if package is None and docassemble.base.functions.this_thread.current_question is not None:
        package = docassemble.base.functions.this_thread.current_question.package
    if thename is None:
        objects = DAList('objects')
        objects.set_random_instance_name()
    else:
        objects = DAList(thename)
    new_objects = recurse_obj(data, recursive=recursive, use_objects=True)
    objects.gathered = True
    objects.revisit = True
    is_singular = True
    if isinstance(new_objects, list):
        is_singular = False
        for obj in new_objects:
            objects.append(obj)
    else:
        objects.append(new_objects)
    if is_singular and len(objects.elements) == 1:
        objects = objects.elements[0]
    if thename is not None and isinstance(objects, DAObject):
        objects._set_instance_name_recursively(thename)
    if isinstance(objects, (DAList, DADict, DASet)) and not gathered:
        objects._reset_gathered_recursively()
    return objects


def objects_from_file(file_ref, recursive=True, gathered=True, name=None, use_objects=False, package=None):
    """Load and return objects from a YAML or JSON source file in the ``sources`` folder.

    Args:
        file_ref (DAFile, DAFileList, DAFileCollection, or int): Reference to
            the file containing the object data.
        recursive (bool): If True (default), recursively convert nested
            structures into docassemble objects.
        gathered (bool): If True (default), mark resulting collections as
            gathered. If False, reset gathered state so the interview can
            prompt for more items.
        name (str or None): Instance name to assign to the returned object.
            If None, the variable name at the call site is used.
        use_objects (bool): If True, convert dicts and lists into DADict and
            DAList objects instead of plain Python types.
        package (str or None): Package context for locating the file. Defaults
            to the current interview's package.

    Returns:
        DAObject, DAList, DADict, or a plain value: The deserialized object(s).

    Raises:
        DAError: If no file reference is provided.
        SystemError: If the referenced file cannot be found.
    """
    if isinstance(file_ref, DAFileCollection):
        file_ref = file_ref._first_file()
    if isinstance(file_ref, DAFileList) and len(file_ref.elements):
        file_ref = file_ref.elements[0]
    if file_ref is None:
        raise DAError("objects_from_file: no file referenced")
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
        objects = DAList('objects')
        objects.set_random_instance_name()
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
                if use_objects:
                    return DAList('return_object', elements=objects)
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
    """A hyperlink to a URL that renders appropriately in each output context.

    Attributes:
        url (str): The destination URL.
        anchor_text (str): The visible link text.
    """

    def __str__(self):
        return str(self.show())

    def show(self):
        """Return a hyperlink rendered for the current output context.

        Returns:
            str or docx Run: A DOCX hyperlink object when evaluated inside a
                DOCX template; a Markdown hyperlink string otherwise.
        """
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return docassemble.base.file_docx.create_hyperlink(self.url, self.anchor_text, docassemble.base.functions.this_thread.misc.get('docx_template', None))
        return '[%s](%s)' % (self.anchor_text, self.url)


class DAContext(DADict):
    """A context-sensitive value that renders differently depending on the output format.

    When converted to a string, the value appropriate for the current output
    context (``question``, ``docx``, ``pdf``, ``pandoc``, or ``document``) is
    returned.

    Attributes:
        question (str): Text used in interview questions (default context).
        document (str): Text used in PDF and DOCX document contexts when no
            more-specific key is present.
        docx (str): Text used in DOCX documents (overrides ``document``).
        pdf (str): Text used in PDF documents (overrides ``document``).
        pandoc (str): Text used in Pandoc-rendered documents (overrides
            ``document``).
    """

    def init(self, *pargs, **kwargs):
        super().init()
        self.pargs = pargs
        self.kwargs = kwargs
        if len(pargs) == 1:
            self['question'] = pargs[0]
            self['document'] = pargs[0]
        if len(pargs) >= 2:
            self['question'] = pargs[0]
            self['document'] = pargs[1]
        for key, val in kwargs.items():
            self[key] = val

    def __str__(self):
        if isinstance(docassemble.base.functions.this_thread.evaluation_context, str) and docassemble.base.functions.this_thread.evaluation_context.startswith('pandoc'):
            context = 'pandoc'
        else:
            context = docassemble.base.functions.this_thread.evaluation_context
        if context in ('docx', 'pdf', 'pandoc'):
            if context in self.elements:
                return str(self.elements[context])
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


def objects_from_structure(target, root=None, gathered=True):
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
            new_dict[key] = objects_from_structure(val, gathered=gathered)
        if gathered:
            new_dict.gathered = True
        if root:
            new_dict._set_instance_name_recursively(root)
        return new_dict
    if isinstance(target, list):
        new_list = DAList('abc_list')
        for val in target.__iter__():  # pylint: disable=unnecessary-dunder-call
            new_list.append(objects_from_structure(val), gathered=gathered)
        if gathered:
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
    """An object whose attributes are persisted in unencrypted global storage outside the interview session.

    Attributes saved on this object are written to a server-side SQL store keyed
    by ``base`` and ``key``, and are restored automatically each time the object
    is unpickled.

    Attributes:
        base (str): Storage scope — ``'user'`` (per-user), ``'interview'``
            (per-interview), or ``'global'`` (site-wide). Defaults to
            ``'user'``.
        key (str): Unique identifier for this object within the chosen base.
            Defaults to a random 32-character alphanumeric string.
    """

    @classmethod
    def keys(cls, base):
        if base == 'interview':
            globalbase = 'da:daglobal:i:' + str(docassemble.base.functions.this_thread.current_info.get('yaml_filename', ''))
        elif base == 'global':
            globalbase = 'da:daglobal:global'
        else:
            globalbase = 'da:daglobal:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id'])
        return server.server_sql_keys(globalbase + ':')

    @classmethod
    def defined(cls, base, key):
        """Return True if a DAGlobal value exists for the given base and key.

        Args:
            base (str): Storage scope (``'user'``, ``'interview'``, or
                ``'global'``).
            key (str): The key to look up.

        Returns:
            bool: True if the key exists; False otherwise.
        """
        if base == 'interview':
            globalkey = 'da:daglobal:i:' + str(docassemble.base.functions.this_thread.current_info.get('yaml_filename', '')) + ':' + str(key)
        elif base == 'global':
            globalkey = 'da:daglobal:global:' + str(key)
        else:
            globalkey = 'da:daglobal:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id']) + ':' + str(key)
        return server.server_sql_defined(globalkey)

    @classmethod
    def remove(cls, base, key):
        """Delete the stored value for the given base and key.

        Args:
            base (str): Storage scope (``'user'``, ``'interview'``, or
                ``'global'``).
            key (str): The key to delete.
        """
        if base == 'interview':
            globalkey = 'da:daglobal:i:' + str(docassemble.base.functions.this_thread.current_info.get('yaml_filename', '')) + ':' + str(key)
        elif base == 'global':
            globalkey = 'da:daglobal:global:' + str(key)
        else:
            globalkey = 'da:daglobal:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id']) + ':' + str(key)
        server.server_sql_delete(globalkey)

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        if 'base' not in kwargs:
            self.base = 'user'
        if 'key' not in kwargs:
            self.key = random_alphanumeric(32)
        if self.base == 'interview':
            globalkey = 'da:daglobal:i:' + str(docassemble.base.functions.this_thread.current_info.get('yaml_filename', '')) + ':' + str(self.key)
        elif self.base == 'global':
            globalkey = 'da:daglobal:global:' + str(self.key)
        else:
            globalkey = 'da:daglobal:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id']) + ':' + str(self.key)
        saved_dict = server.server_sql_get(globalkey)  # pylint: disable=assignment-from-none
        if isinstance(saved_dict, dict):
            for key, val in saved_dict.items():
                setattr(self, key, val)

    def __getstate__(self):
        if hasattr(self, 'base') and hasattr(self, 'key'):
            if self.base == 'interview':
                globalkey = 'da:daglobal:i:' + str(docassemble.base.functions.this_thread.current_info.get('yaml_filename', '')) + ':' + str(self.key)
            elif self.base == 'global':
                globalkey = 'da:daglobal:global:' + str(self.key)
            else:
                globalkey = 'da:daglobal:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id']) + ':' + str(self.key)
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
                globalkey = 'da:daglobal:i:' + str(docassemble.base.functions.this_thread.current_info.get('yaml_filename', '')) + ':' + str(pickle_dict['key'])
            elif pickle_dict['base'] == 'global':
                globalkey = 'da:daglobal:global:' + str(pickle_dict['key'])
            else:
                globalkey = 'da:daglobal:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id']) + ':' + str(pickle_dict['key'])

            saved_dict = server.server_sql_get(globalkey)  # pylint: disable=assignment-from-none
            if isinstance(saved_dict, dict):
                for key, val in saved_dict.items():
                    setattr(self, key, val)

    def delete(self):
        """Delete all data from global storage and undefine all object attributes."""
        if hasattr(self, 'base') and hasattr(self, 'key'):
            if self.base == 'interview':
                globalkey = 'da:daglobal:i:' + docassemble.base.functions.this_thread.current_info.get('yaml_filename', '') + ':' + self.key
            elif self.base == 'global':
                globalkey = 'da:daglobal:global:' + self.key
            else:
                globalkey = 'da:daglobal:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id']) + ':' + self.key
            server.server_sql_delete(globalkey)
            self.__dict__ = {'instanceName': self.instanceName, 'attrList': [], 'has_nonrandom_instance_name': self.has_nonrandom_instance_name}


class DAStore(DAObject):
    """A key-value store backed by server-side SQL, with optional encryption.

    Attributes:
        base (str): Storage scope — ``'user'`` (per-user, encrypted),
            ``'interview'`` (per-interview, unencrypted), ``'session'``
            (per-session, encrypted), ``'global'`` (site-wide, unencrypted),
            or a custom string prefix. Defaults to ``'user'``.
        encrypted (bool): If set, overrides the default encryption behavior
            for the chosen ``base``.
    """

    def is_encrypted(self):
        """Return True if data is stored with encryption.

        Returns:
            bool: True if encryption is enabled for this store.
        """
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
                return 'da:i:' + docassemble.base.functions.this_thread.current_info.get('yaml_filename', '')
            if self.base == 'user':
                return 'da:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id'])
            if self.base == 'session':
                return 'da:uid:' + get_uid() + ':i:' + docassemble.base.functions.this_thread.current_info.get('yaml_filename', '')
            if self.base == 'global':
                return 'da:global'
            return str(self.base)
        return 'da:userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id'])

    def defined(self, key):
        """Return True if the given key exists in the store.

        Args:
            key (str): Key to check.

        Returns:
            bool: True if the key exists; False otherwise.
        """
        the_key = self._get_base_key() + ':' + key
        return server.server_sql_defined(the_key)

    def get(self, key):
        """Retrieve the value stored under the given key.

        Args:
            key (str): Key to retrieve.

        Returns:
            object: The stored value, or None if not found.
        """
        the_key = self._get_base_key() + ':' + key
        return server.server_sql_get(the_key, secret=docassemble.base.functions.this_thread.current_info.get('secret', None))

    def set(self, key, the_value):
        """Store a value under the given key.

        Args:
            key (str): Key under which to store the value.
            the_value (object): Value to store.
        """
        the_key = self._get_base_key() + ':' + key
        server.server_sql_set(the_key, the_value, encrypted=self.is_encrypted(), secret=docassemble.base.functions.this_thread.current_info.get('secret', None), the_user_id=docassemble.base.functions.this_thread.current_info['user']['the_user_id'])

    def delete(self, key):
        """Delete the value stored under the given key.

        Args:
            key (str): Key to delete.
        """
        the_key = self._get_base_key() + ':' + key
        server.server_sql_delete(the_key)

    def keys(self):
        """Return a list of all keys currently stored.

        Returns:
            list[str]: Keys present in this store.
        """
        return server.server_sql_keys(self._get_base_key() + ':')


class BearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        if "Authorization" not in r.headers:
            r.headers["Authorization"] = "Bearer " + str(self.token)
        return r


class DAWeb(DAObject):
    """An HTTP client for calling external REST APIs from an interview.

    Attributes:
        base_url (str): Base URL prepended to relative paths passed to HTTP
            methods.
        headers (dict): Default request headers merged into every call.
        cookies (dict): Default cookies sent with every call and updated from
            each response.
        auth (dict): Authentication credentials. The ``type`` key selects the
            scheme (``'basic'``, ``'digest'``, or ``'bearer'``).
        json_body (bool): If True (the default), POST/PUT/PATCH bodies are
            sent as JSON; otherwise as form-encoded data.
        on_failure: Default value returned (or exception raised) when a
            request fails. Use ``'raise'`` to raise a ``DAWebError``.
        on_success: Default value returned on success. By default the parsed
            JSON response (or raw text) is returned.
        success_code (int or list[int]): HTTP status code(s) considered
            successful. Defaults to any 2xx code.
        task (str): Interview task name to mark as performed on success.
    """

    def _get_base_url(self):
        if hasattr(self, 'base_url'):
            base_url = self.base_url
            if not isinstance(self.base_url, str):
                raise DAError("DAWeb.call: the base url must be a string")
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
            raise DAError("DAWeb.call: task must be a string")
        return task

    def _get_task_persistent(self, task_persistent):
        if task_persistent is None and hasattr(self, 'task_persistent'):
            task_persistent = self.task_persistent
        if task_persistent is None:
            return False
        if not isinstance(task_persistent, (bool, str)):
            raise DAError("DAWeb.call: task_persistent must be boolean or string")
        return task_persistent

    def _get_auth(self, auth):
        if auth is None and hasattr(self, 'auth'):
            auth = self.auth
        if isinstance(auth, (dict, DADict)):
            if auth.get('type', 'basic') == 'basic':
                return HTTPBasicAuth(auth['username'], auth['password'])
            if auth['type'] == 'digest':
                return HTTPDigestAuth(auth['username'], auth['password'])
            if auth['type'] == 'bearer':
                return BearerAuth(auth['token'])
        return auth

    def _get_headers(self, new_headers):
        if hasattr(self, 'headers'):
            headers = self.headers
            if isinstance(headers, DADict):
                headers = headers.elements
            if not isinstance(headers, dict):
                raise DAError("DAWeb.call: the headers must be a dictionary")
            headers.update(new_headers)
            return headers
        return new_headers

    def _get_cookies(self, new_cookies):
        if hasattr(self, 'cookies'):
            cookies = self.cookies
            if isinstance(cookies, DADict):
                cookies = cookies.elements
            if not isinstance(cookies, dict):
                raise DAError("DAWeb.call: the cookies must be a dictionary")
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
                    raise DAError("DAWeb.call: success codes must be integers")
                new_success_code.append(code)
            success_code = new_success_code
        elif isinstance(success_code, int):
            success_code = [success_code]
        elif success_code is not None:
            raise DAError("DAWeb.call: success_code must be an integer or a list of integers")
        if method is None:
            method = 'GET'
        if not isinstance(method, str):
            raise DAError("DAWeb.call: the method must be a string")
        method = method.upper().strip()
        if method not in ('POST', 'GET', 'PATCH', 'PUT', 'HEAD', 'DELETE', 'OPTIONS'):
            raise DAError("DAWeb.call: invalid method")
        if not isinstance(url, str):
            raise DAError("DAWeb.call: the url must be a string")
        if not re.search(r'^https?://', url):
            url = self._get_base_url() + re.sub(r'^/*', '', url)
        if data is None:
            data = {}
        if isinstance(data, DADict):
            data = data.elements
        # if json_body is False and not isinstance(data, dict):
        #     raise DAError("DAWeb.call: data must be a dictionary")
        if params is None:
            params = {}
        if isinstance(params, DADict):
            params = params.elements
        if not isinstance(params, dict):
            raise DAError("DAWeb.call: params must be a dictionary")
        if headers is None:
            headers = {}
        if isinstance(headers, DADict):
            headers = headers.elements
        if not isinstance(headers, dict):
            raise DAError("DAWeb.call: the headers must be a dictionary")
        headers = self._get_headers(headers)
        if len(headers) == 0:
            headers = None
        if cookies is None:
            cookies = {}
        if isinstance(cookies, DADict):
            cookies = cookies.elements
        if not isinstance(cookies, dict):
            raise DAError("DAWeb.call: the cookies must be a dictionary")
        cookies = self._get_cookies(cookies)
        if len(cookies) == 0:
            cookies = None
        if isinstance(data, dict) and len(data) == 0:
            data = None
        if files is not None:
            if not isinstance(files, dict):
                raise DAError("DAWeb.call: files must be a dictionary")
            new_files = {}
            for key, val in files.items():
                if not isinstance(key, str):
                    raise DAError("DAWeb.call: files must be a dictionary of string keys")
                try:
                    path = server.path_from_reference(val)
                    logmessage("path is " + str(path))
                    assert path is not None
                except:
                    raise DAError("DAWeb.call: could not load the file")
                new_files[key] = open(path, 'rb')
            files = new_files
            if len(files):
                json_body = False
        try:
            if method == 'POST':
                if json_body:
                    r = requests.post(url, json=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files, timeout=600)
                else:
                    r = requests.post(url, data=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files, timeout=600)
            elif method == 'PUT':
                if json_body:
                    r = requests.put(url, json=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files, timeout=600)
                else:
                    r = requests.put(url, data=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files, timeout=600)
            elif method == 'PATCH':
                if json_body:
                    r = requests.patch(url, json=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files, timeout=600)
                else:
                    r = requests.patch(url, data=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files, timeout=600)
            elif method == 'GET':
                if len(params) == 0:
                    params = data
                    data = None
                r = requests.get(url, params=params, headers=headers, auth=auth, cookies=cookies, timeout=600)
            elif method == 'DELETE':
                if len(params) == 0:
                    params = data
                    data = None
                r = requests.delete(url, params=params, headers=headers, auth=auth, cookies=cookies, timeout=600)
            elif method == 'OPTIONS':
                if len(params) == 0:
                    params = data
                    data = None
                r = requests.options(url, params=params, headers=headers, auth=auth, cookies=cookies, timeout=600)
            else:  # method == 'HEAD'
                if len(params) == 0:
                    params = data
                    data = None
                r = requests.head(url, params=params, headers=headers, auth=auth, cookies=cookies, timeout=600)
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
        """Send an HTTP GET request.

        Args:
            url (str): Target URL or path relative to ``base_url``.
            data (dict): Query parameters (merged with ``params``).
            params (dict): URL query parameters.
            headers (dict): Additional request headers.
            json_body (bool): Ignored for GET (no body).
            on_failure: Value to return on failure, or ``'raise'``.
            on_success: Value to return on success (default: parsed JSON or text).
            auth: Authentication credentials.
            cookies (dict): Additional cookies.
            task (str): Task name to mark as performed on success.
            task_persistent (bool): If True, the task persists across sessions.

        Returns:
            object: Parsed JSON response, raw text, or the ``on_failure``/
                ``on_success`` value.
        """
        return self._call(url, method='GET', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent)

    def post(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None, files=None):
        """Send an HTTP POST request.

        Args:
            url (str): Target URL or path relative to ``base_url``.
            data (dict): Request body data.
            params (dict): URL query parameters.
            headers (dict): Additional request headers.
            json_body (bool): If True (default), send body as JSON.
            on_failure: Value to return on failure, or ``'raise'``.
            on_success: Value to return on success.
            auth: Authentication credentials.
            cookies (dict): Additional cookies.
            task (str): Task name to mark as performed on success.
            task_persistent (bool): If True, the task persists across sessions.
            files (dict): Files to upload, mapping field names to file objects.

        Returns:
            object: Parsed JSON response, raw text, or the ``on_failure``/
                ``on_success`` value.
        """
        return self._call(url, method='POST', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent, files=files)

    def put(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None, files=None):
        """Send an HTTP PUT request.

        Args:
            url (str): Target URL or path relative to ``base_url``.
            data (dict): Request body data.
            params (dict): URL query parameters.
            headers (dict): Additional request headers.
            json_body (bool): If True (default), send body as JSON.
            on_failure: Value to return on failure, or ``'raise'``.
            on_success: Value to return on success.
            auth: Authentication credentials.
            cookies (dict): Additional cookies.
            task (str): Task name to mark as performed on success.
            task_persistent (bool): If True, the task persists across sessions.
            files (dict): Files to upload.

        Returns:
            object: Parsed JSON response, raw text, or the ``on_failure``/
                ``on_success`` value.
        """
        return self._call(url, method='PUT', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent, files=files)

    def patch(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None, files=None):
        """Send an HTTP PATCH request.

        Args:
            url (str): Target URL or path relative to ``base_url``.
            data (dict): Request body data.
            params (dict): URL query parameters.
            headers (dict): Additional request headers.
            json_body (bool): If True (default), send body as JSON.
            on_failure: Value to return on failure, or ``'raise'``.
            on_success: Value to return on success.
            auth: Authentication credentials.
            cookies (dict): Additional cookies.
            task (str): Task name to mark as performed on success.
            task_persistent (bool): If True, the task persists across sessions.
            files (dict): Files to upload.

        Returns:
            object: Parsed JSON response, raw text, or the ``on_failure``/
                ``on_success`` value.
        """
        return self._call(url, method='PATCH', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent, files=files)

    def delete(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None):
        """Send an HTTP DELETE request.

        Args:
            url (str): Target URL or path relative to ``base_url``.
            data (dict): Query parameters.
            params (dict): URL query parameters.
            headers (dict): Additional request headers.
            json_body (bool): Ignored for DELETE.
            on_failure: Value to return on failure, or ``'raise'``.
            on_success: Value to return on success.
            auth: Authentication credentials.
            cookies (dict): Additional cookies.
            task (str): Task name to mark as performed on success.
            task_persistent (bool): If True, the task persists across sessions.

        Returns:
            object: Parsed JSON response, raw text, or the ``on_failure``/
                ``on_success`` value.
        """
        return self._call(url, method='DELETE', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent)

    def options(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None):
        """Send an HTTP OPTIONS request.

        Args:
            url (str): Target URL or path relative to ``base_url``.
            data (dict): Query parameters.
            params (dict): URL query parameters.
            headers (dict): Additional request headers.
            json_body (bool): Ignored for OPTIONS.
            on_failure: Value to return on failure, or ``'raise'``.
            on_success: Value to return on success.
            auth: Authentication credentials.
            cookies (dict): Additional cookies.
            task (str): Task name to mark as performed on success.
            task_persistent (bool): If True, the task persists across sessions.

        Returns:
            object: Parsed JSON response, raw text, or the ``on_failure``/
                ``on_success`` value.
        """
        return self._call(url, method='OPTIONS', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent)

    def head(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None):
        """Send an HTTP HEAD request.

        Args:
            url (str): Target URL or path relative to ``base_url``.
            data (dict): Query parameters.
            params (dict): URL query parameters.
            headers (dict): Additional request headers.
            json_body (bool): Ignored for HEAD.
            on_failure: Value to return on failure, or ``'raise'``.
            on_success: Value to return on success.
            auth: Authentication credentials.
            cookies (dict): Additional cookies.
            task (str): Task name to mark as performed on success.
            task_persistent (bool): If True, the task persists across sessions.

        Returns:
            object: Parsed JSON response, raw text, or the ``on_failure``/
                ``on_success`` value.
        """
        return self._call(url, method='HEAD', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent)


class DARedis(DAObject):
    """An interface for reading and writing data in the Redis cache.

    Provides convenience wrappers for pickling Python objects to Redis and
    exposes the raw ``redis-py`` client via attribute access.
    """

    def key(self, keyname):
        """Return a namespaced Redis key prefixed with the current interview name.

        Args:
            keyname (str): Suffix to append to the interview-based prefix.

        Returns:
            str: Fully qualified Redis key.
        """
        return docassemble.base.functions.this_thread.current_info.get('yaml_filename', '') + ':' + str(keyname)

    def get_data(self, key):
        """Retrieve and unpickle a Python object stored in Redis.

        Args:
            key (str): Redis key.

        Returns:
            object: Unpickled value, or None if the key does not exist or
                unpickling fails.
        """
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
        """Pickle and store a Python object in Redis.

        Args:
            key (str): Redis key under which to store the value.
            data (object): Python object to pickle and store.
            expire (int or None): Optional TTL in seconds. If None, the key
                does not expire.

        Raises:
            DAError: If ``expire`` is provided but is not an integer.
        """
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
    """An interface for interacting with cloud object storage (S3 or Azure Blob Storage).

    Attributes:
        provider (str): Cloud provider identifier (used only for custom
            configurations).
        config (dict): Provider-specific configuration (used only for custom
            configurations).
    """

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
        """The underlying cloud connection object (``boto3.resource('s3')`` or ``BlockBlobService``)."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).conn
        return server.cloud.conn

    @property
    def client(self):
        """The ``boto3.client('s3')`` object for low-level S3 operations."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).client
        return server.cloud.client

    @property
    def bucket(self):
        """The ``boto3 Bucket`` object for the configured S3 bucket."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).bucket
        return server.cloud.bucket

    @property
    def bucket_name(self):
        """The name of the Amazon S3 bucket."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).bucket_name
        return server.cloud.bucket_name

    @property
    def container_name(self):
        """The name of the Azure Blob Storage container."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).container
        return server.cloud.container


class BackgroundAction(DAObject):
    """Manages a long-running Celery background action from within an interview.

    On first access the background action is dispatched and the interview
    shows a wait screen; on subsequent accesses the result is returned once
    the action completes.

    Attributes:
        refresh_seconds (int): Seconds between wait-screen refresh polls.
            Defaults to 4.
    """

    def init(self, *pargs, **kwargs):
        self._running = False
        self.refresh_seconds = 4
        super().init(*pargs, **kwargs)

    def run(self, action, **pargs):
        if in_celery:
            raise DAException("You cannot run a BackgroundAction inside of a background action")
        if not self._running:
            self.bg_action = background_action(action, **pargs)
            self._running = True
            self.initial_wait()
        if self._running:
            if not self.bg_action.ready():
                self.wait()
            result = self.bg_action.result()
            failed = self.bg_action.failed()
            del self.bg_action
            self._running = False
            if failed:
                return self.on_failure(result)
            return self.process_response(result)
        return None

    def initial_wait(self):
        command('wait', sleep=self.refresh_seconds)

    def wait(self):
        set_save_status('ignore')
        command('wait', sleep=self.refresh_seconds)

    def process_response(self, result):
        return result.value

    def on_failure(self, result):
        return result.value

    def running(self):
        return self._running

    def ready(self):
        if self._running:
            return self.bg_action.ready()
        return None


class DAGoogleAPI(DAObject):
    """A helper for accessing Google APIs using service-account credentials.

    Provides factory methods that return authenticated client objects for
    Google Drive, Sheets, Cloud Storage, and Cloud Vision.
    """

    def api_credentials(self, scope):
        """Return an OAuth2 credentials object for the given API scope.

        Args:
            scope (str): OAuth2 scope URL.

        Returns:
            google.oauth2.credentials.Credentials: Authenticated credentials.
        """
        return server.google_api().google_api_credentials(scope)

    def http(self, scope):
        """Return an authorized ``httplib2.Http`` object for the given API scope.

        Args:
            scope (str): OAuth2 scope URL.

        Returns:
            google_auth_httplib2.AuthorizedHttp: Authorized HTTP transport.
        """
        return google_auth_httplib2.AuthorizedHttp(self.cloud_credentials(scopes=[scope]), http=httplib2.Http())

    def drive_service(self):
        """Return an authenticated Google Drive v3 service object.

        Returns:
            googleapiclient.discovery.Resource: Authorized Drive service.
        """
        import apiclient
        return apiclient.discovery.build('drive', 'v3', http=self.http('https://www.googleapis.com/auth/drive'))

    def sheets_service(self):
        """Return an authenticated Google Sheets v4 service object.

        Returns:
            googleapiclient.discovery.Resource: Authorized Sheets service.
        """
        import apiclient
        return apiclient.discovery.build('sheets', 'v4', http=self.http('https://www.googleapis.com/auth/spreadsheets.readonly'))

    def cloud_credentials(self, scopes=None):
        """Return Google Cloud service-account credentials.

        Args:
            scopes (list[str] or None): OAuth2 scopes to request. If None,
                uses the default scopes configured on the service account.

        Returns:
            google.oauth2.service_account.Credentials: Service account
                credentials.
        """
        return server.google_api().google_cloud_credentials(scopes=scopes)

    def project_id(self):
        """Return the Google Cloud project ID from the service-account credentials.

        Returns:
            str: Google Cloud project ID.
        """
        return server.google_api().project_id()

    def google_cloud_storage_client(self):
        """Return an authenticated Google Cloud Storage client.

        Returns:
            google.cloud.storage.Client: Authorized Cloud Storage client.
        """
        return server.google_api().google_cloud_storage_client()

    def google_cloud_vision_client(self):
        """Return an authenticated Google Cloud Vision client.

        Returns:
            google.cloud.vision.ImageAnnotatorClient: Authorized Vision client.
        """
        return server.google_api().google_cloud_vision_client()


def run_python_module(module, arguments=None):
    """Run a Python module as a subprocess and return its output.

    Args:
        module (str): Dotted module name or a ``.py`` filename (resolved
            relative to the current package). A leading ``.`` is treated as
            a relative import.
        arguments (list or None): Command-line arguments to pass to the
            module.

    Returns:
        tuple[str, int]: A 2-tuple of ``(output, return_code)`` where
            ``output`` is the combined stdout/stderr text and ``return_code``
            is the process exit code (0 on success).

    Raises:
        DAError: If ``arguments`` is not a list.
    """
    if re.search(r'\.py$', module):
        module = docassemble.base.functions.this_thread.current_package + '.' + re.sub(r'\.py$', '', module)
    elif re.search(r'^\.', module):
        module = docassemble.base.functions.this_thread.current_package + module
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
    """Return today's date at midnight as a DADateTime object.

    Args:
        timezone (str or None): IANA timezone name. If None, the interview's
            default timezone is used.
        format (str or None): If provided, return the date formatted as a
            string using this Babel date-format pattern instead of a
            DADateTime.

    Returns:
        DADateTime or str: Midnight today in the given timezone, or a
            formatted date string if ``format`` is specified.
    """
    ensure_definition(timezone, format)
    if timezone is None:
        timezone = get_default_timezone()
    val = datetime.datetime.now(datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone))
    if format is not None:
        return dd(val.replace(hour=0, minute=0, second=0, microsecond=0)).format_date(format)
    return dd(val.replace(hour=0, minute=0, second=0, microsecond=0))


def babel_language(language):
    if 'babel dates map' not in server.daconfig:
        return language
    return server.daconfig['babel dates map'].get(language, language)


def month_of(the_date, as_word=False, language=None):
    """Return the month component of a date.

    Args:
        the_date (datetime.date, datetime.datetime, or str): The date to
            extract the month from.
        as_word (bool): If True, return the full month name (e.g.
            ``'January'``); otherwise return the month as an integer.
        language (str or None): Language code for localizing the month name.
            Defaults to the current interview language.

    Returns:
        int or str: Month number (1–12) or localized month name.
    """
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
    """Return the day-of-month component of a date.

    Args:
        the_date (datetime.date, datetime.datetime, or str): The date to
            extract the day from.
        language (str or None): Unused; retained for API consistency.

    Returns:
        int: Day of the month (1–31).
    """
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
    """Return the day of the week for a date.

    Args:
        the_date (datetime.date, datetime.datetime, or str): The date to
            inspect.
        as_word (bool): If True, return the full weekday name (e.g.
            ``'Monday'``); otherwise return an integer from 1 (Monday) to
            7 (Sunday) per ISO 8601.
        language (str or None): Language code for localizing the weekday
            name. Defaults to the current interview language.

    Returns:
        int or str: Day-of-week number or localized weekday name.
    """
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
    """Return the year component of a date.

    Args:
        the_date (datetime.date, datetime.datetime, or str): The date to
            extract the year from.
        language (str or None): Unused; retained for API consistency.

    Returns:
        int: Four-digit year.
    """
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
    if the_part in docassemble.base.functions.this_thread.internal and docassemble.base.functions.this_thread.internal[the_part] is not None:
        return docassemble.base.functions.this_thread.internal[the_part]
    for lang in (language, get_language(), '*'):
        if lang is not None and docassemble.base.functions.this_thread.interview is not None and lang in docassemble.base.functions.this_thread.interview.default_title and the_part in docassemble.base.functions.this_thread.interview.default_title[lang]:
            return docassemble.base.functions.this_thread.interview.default_title[lang][the_part]
    return default_value


def format_date(the_date, format=None, language=None):  # pylint: disable=redefined-builtin
    """Return a date formatted as a localized string.

    Args:
        the_date (datetime.date, datetime.datetime, or str): Date to format.
        format (str or None): Babel date-format pattern (e.g. ``'long'``,
            ``'short'``, ``'MM/dd/yyyy'``). Defaults to the interview's
            configured date format or ``'long'``.
        language (str or None): Language/locale code. Defaults to the current
            interview language.

    Returns:
        str: Formatted date string, or ``''`` for an empty date.
    """
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
    """Return a date and time formatted as a localized string.

    Args:
        the_date (datetime.datetime or str): Date/time to format.
        format (str or None): Babel datetime-format pattern. Defaults to the
            interview's configured datetime format or ``'long'``.
        language (str or None): Language/locale code. Defaults to the current
            interview language.

    Returns:
        str: Formatted datetime string, or ``''`` for an empty date.
    """
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
    """Return a time formatted as a localized string.

    Args:
        the_time (datetime.time, datetime.datetime, or str): Time to format.
        format (str or None): Babel time-format pattern. Defaults to the
            interview's configured time format or ``'short'``.
        language (str or None): Language/locale code. Defaults to the current
            interview language.

    Returns:
        str: Formatted time string, or ``''`` for an empty time.
    """
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
    except BaseException as errmess:
        return word("Bad date: " + str(errmess))


class DateTimeDelta:

    def __str__(self):
        return str(self.describe())

    def describe(self, **kwargs):
        specificity = kwargs.get('specificity', None)
        output = []
        diff = dateutil.relativedelta.relativedelta(self.end, self.start)
        if diff.years != 0:
            output.append((abs(diff.years), noun_plural(word('year'), abs(diff.years), noun_is_singular=True)))
        if diff.months != 0 and specificity != 'year':
            output.append((abs(diff.months), noun_plural(word('month'), abs(diff.months), noun_is_singular=True)))
        if diff.days != 0 and specificity not in ('year', 'month'):
            output.append((abs(diff.days), noun_plural(word('day'), abs(diff.days), noun_is_singular=True)))
        if len(output) == 0 or specificity in ('hour', 'minute', 'second'):
            if diff.hours != 0 and specificity not in ('year', 'month', 'day'):
                output.append((abs(diff.hours), noun_plural(word('hour'), abs(diff.hours), noun_is_singular=True)))
            if (abs(diff.hours) < 2 or specificity in ('minute', 'second')) and diff.minutes != 0 and specificity not in ('year', 'month', 'day', 'hour'):
                output.append((abs(diff.minutes), noun_plural(word('minute'), abs(diff.minutes), noun_is_singular=True)))
        if len(output) == 0 or specificity == 'second':
            if diff.seconds != 0 and specificity not in ('year', 'month', 'day', 'hour', 'minute'):
                output.append((abs(diff.seconds), noun_plural(word('second'), abs(diff.seconds), noun_is_singular=True)))
        if len(output) == 0:
            if specificity is None:
                output.append((0, noun_plural(word('second'), 0, noun_is_singular=True)))
            else:
                output.append((0, noun_plural(word(specificity), 0, noun_is_singular=True)))
        if kwargs.get('nice', True):
            return_value = comma_and_list(["%s %s" % (nice_number(y[0]), y[1]) for y in output])
            if kwargs.get('capitalize', False):
                return capitalize(return_value)
            return return_value
        return comma_and_list(["%d %s" % y for y in output])


class DADateTime(datetime.datetime):
    """A timezone-aware datetime subclass with docassemble-specific formatting and arithmetic.

    Inherits all ``datetime.datetime`` behavior and adds convenience methods
    for formatting, date arithmetic, and accessing ISO calendar properties.

    Attributes:
        dow (int): Day of the week (1 = Monday … 7 = Sunday, ISO 8601).
        week (int): ISO week number of the year.
        nanosecond (int): Always 0; provided for compatibility.
    """

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
    """Return the current date and time as a DADateTime object.

    Args:
        timezone (str or None): IANA timezone name. If None, the interview's
            default timezone is used.

    Returns:
        DADateTime: Current date and time in the specified timezone.
    """
    ensure_definition(timezone)
    if timezone is None:
        timezone = get_default_timezone()
    return dd(datetime.datetime.now(datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)))


def as_datetime(the_date, timezone=None):
    """Convert a date or date string to a timezone-aware DADateTime object.

    Args:
        the_date (datetime.date, datetime.datetime, or str): Date or
            date/time value to convert. String values are parsed with
            ``dateutil``.
        timezone (str or None): IANA timezone name to attach. If the value
            already carries timezone information it is converted to this
            zone; otherwise the timezone is applied as-is. Defaults to
            the interview's default timezone.

    Returns:
        DADateTime: Timezone-aware datetime.
    """
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
    """Return a relative date/time interval.

    All keyword arguments are forwarded to
    ``dateutil.relativedelta.relativedelta``. Common arguments include
    ``years``, ``months``, ``weeks``, ``days``, ``hours``, ``minutes``,
    and ``seconds``.

    Returns:
        dateutil.relativedelta.relativedelta: Interval that can be added to
            or subtracted from a ``DADateTime`` or ``datetime`` object.
    """
    ensure_definition(**kwargs)
    return dateutil.relativedelta.relativedelta(**kwargs)


def date_difference(starting=None, ending=None, timezone=None):
    """Return the difference between two dates.

    Args:
        starting (datetime.date, datetime.datetime, str, or None): Start of
            the interval. Defaults to the current datetime.
        ending (datetime.date, datetime.datetime, str, or None): End of the
            interval. Defaults to the current datetime.
        timezone (str or None): IANA timezone name used when localizing
            naive datetimes. Defaults to the interview's default timezone.

    Returns:
        DateTimeDelta: Object with ``weeks``, ``days``, ``hours``,
            ``minutes``, ``seconds``, ``years``, and ``delta`` attributes
            expressing the difference, and ``start``/``end`` attributes
            holding the resolved datetime objects.
    """
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
    """Return a sorted list of all available IANA timezone names.

    Returns:
        list[str]: Sorted list of timezone strings (e.g. ``'America/New_York'``).
    """
    return sorted(list(zoneinfo.available_timezones()))


def returning_user(minutes=None, hours=None, days=None):
    """Return True if the user is returning after a period of inactivity.

    Args:
        minutes (float or None): Return True if more than this many minutes
            have elapsed since the last access.
        hours (float or None): Return True if more than this many hours have
            elapsed.
        days (float or None): Return True if more than this many days have
            elapsed.

    Returns:
        bool: True if the user is returning after the specified period (or
            after 6 hours by default); False otherwise or on POST requests.
    """
    if docassemble.base.functions.this_thread.current_info['method'] != 'GET':
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
    """Return the time elapsed since the interview was last accessed.

    Accepts the same arguments as :func:`last_access_time`.

    Returns:
        datetime.timedelta: Elapsed time since last access, or a zero
            timedelta if there is no access record.
    """
    last_time = last_access_time(*pargs, **kwargs)
    if last_time is None:
        return datetime.timedelta(0)
    return current_datetime() - last_time


def last_access_days(*pargs, **kwargs):
    """Return the number of days since the interview was last accessed.

    Accepts the same arguments as :func:`last_access_time`.

    Returns:
        float: Days since last access.
    """
    delta = last_access_delta(*pargs, **kwargs)
    return delta.days + (delta.seconds / 86400.0)


def last_access_hours(*pargs, **kwargs):
    """Return the number of hours since the interview was last accessed.

    Accepts the same arguments as :func:`last_access_time`.

    Returns:
        float: Hours since last access.
    """
    delta = last_access_delta(*pargs, **kwargs)
    return (delta.days * 24.0) + (delta.seconds / 3600.0)


def last_access_minutes(*pargs, **kwargs):
    """Return the number of minutes since the interview was last accessed.

    Accepts the same arguments as :func:`last_access_time`.

    Returns:
        float: Minutes since last access.
    """
    delta = last_access_delta(*pargs, **kwargs)
    return (delta.days * 1440.0) + (delta.seconds / 60.0)


def last_access_time(include_privileges=None, exclude_privileges=None, include_cron=False, timezone=None):
    """Return the most recent time the interview was accessed.

    Args:
        include_privileges (list[str] or str or None): If provided, only
            consider accesses by users with one of these privilege names.
        exclude_privileges (list[str] or str or None): If provided, ignore
            accesses by users with one of these privilege names.
        include_cron (bool): If True, include accesses by cron jobs.
            Defaults to False.
        timezone (str or None): IANA timezone for the returned datetime.
            Defaults to the interview's default timezone.

    Returns:
        DADateTime or None: The most recent access time, or None if no
            matching access record exists.
    """
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
    for user_id, access_time in docassemble.base.functions.this_thread.internal['accesstime'].items():
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
    """Return the time the current interview session was started.

    Args:
        timezone (str or None): IANA timezone name for the returned datetime.
            If None, UTC is used.

    Returns:
        DADateTime: Session start time.
    """
    if timezone is not None:
        return dd(docassemble.base.functions.this_thread.internal['starttime'].replace(tzinfo=datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)))
    return dd(docassemble.base.functions.this_thread.internal['starttime'].replace(tzinfo=datetime.timezone.utc))


class LatitudeLongitude(DAObject):
    """A GPS coordinate obtained from the user's browser.

    Attributes:
        gathered (bool): True once the browser has responded with a location
            or an error.
        known (bool): True if a valid latitude and longitude were obtained.
        latitude (float): Latitude in decimal degrees (set when known).
        longitude (float): Longitude in decimal degrees (set when known).
        error (str): Browser error message (set when the location is
            unavailable).
        description (str): String representation of the location.
    """

    def init(self, *pargs, **kwargs):
        self.gathered = False
        self.known = False
        # self.description = ""
        super().init(*pargs, **kwargs)

    def status(self):
        """Return True if the browser should be asked for the location; False otherwise.

        Returns:
            bool: True if a geolocation request should be sent; False if the
                location has already been gathered or returned.
        """
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
        if 'user' in docassemble.base.functions.this_thread.current_info and 'location' in docassemble.base.functions.this_thread.current_info['user'] and isinstance(docassemble.base.functions.this_thread.current_info['user']['location'], dict):
            if 'latitude' in docassemble.base.functions.this_thread.current_info['user']['location'] and 'longitude' in docassemble.base.functions.this_thread.current_info['user']['location']:
                self.latitude = docassemble.base.functions.this_thread.current_info['user']['location']['latitude']
                self.longitude = docassemble.base.functions.this_thread.current_info['user']['location']['longitude']
                self.known = True
                # logmessage("known is true")
            elif 'error' in docassemble.base.functions.this_thread.current_info['user']['location']:
                self.error = docassemble.base.functions.this_thread.current_info['user']['location']['error']
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
    """Tracks role changes in a multi-user interview to prevent duplicate notifications.

    Stores the last role for which a notification was sent and skips sending
    emails when the required role has not changed.
    """

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
        """Send a role-change notification email if needed.

        Args:
            roles_needed (list[str]): Role names that are now required for the
                interview to proceed.
            **kwargs: Each keyword argument is a role name mapping to a dict
                with ``'to'`` (recipient) and ``'email'`` (DATemplate) keys.
                A ``'config'`` key may specify the email configuration to use.

        Returns:
            bool: True if an email was successfully sent; False if no email
                was necessary or sending failed.
        """
        # logmessage("Current role is " + str(docassemble.base.functions.this_thread.global_vars.role))
        for key, val in kwargs.items():  # pylint: disable=unused-variable
            if 'to' in val:
                need(val['to'].email)
        config = kwargs.get('config', None)
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
                        result = send_email(to=email_info['to'], html=email_info['email'].content, subject=email_info['email'].subject, config=config)
                    except DAError:
                        result = False
                    if result:
                        self._update(role_needed)
                    return result
        return False


class Name(DAObject):
    """Base class for a person's name, backed by a single ``text`` attribute.

    Attributes:
        text (str): The full name as a single string.
    """

    def full(self, **kwargs):  # pylint: disable=unused-argument
        """Return the full name.

        Returns:
            str: The ``text`` attribute of the name.
        """
        return self.text

    def familiar(self):
        """Return the familiar (first) name.

        Returns:
            str: The familiar form of the name.
        """
        return self.text

    def firstlast(self):
        """Return the name in first-last order (compatibility method).

        Returns:
            str: The name text.
        """
        return self.text

    def lastfirst(self):
        """Return the name in last-first order (compatibility method).

        Returns:
            str: The name text.
        """
        return self.text

    def middle_initial(self, with_period=True):  # pylint: disable=unused-argument
        """Return the middle initial (compatibility method; always empty for this class).

        Returns:
            str: Empty string.
        """
        return ''

    def defined(self):
        """Return True if the name has been defined.

        Returns:
            bool: True if the ``text`` attribute exists; False otherwise.
        """
        return hasattr(self, 'text')

    def __str__(self):
        return str(self.full())
#    def __repr__(self):
#        return repr(self.full())


class IndividualName(Name):
    """The name of an Individual, stored as separate parts.

    Attributes:
        uses_parts (bool): If True (the default), the name is assembled from
            ``first``, ``middle``, ``last``, ``suffix``, etc. If False, a
            single ``text`` attribute is used instead.
        first (str): First name.
        middle (str): Middle name (optional).
        last (str): Last name.
        suffix (str): Name suffix such as ``'Jr.'`` (optional).
        paternal_surname (str): Paternal surname (alternative to ``last``).
        maternal_surname (str): Maternal surname (optional).
    """

    def init(self, *pargs, **kwargs):
        if 'uses_parts' not in kwargs:
            self.uses_parts = True
        super().init(*pargs, **kwargs)

    def defined(self):
        """Return True if the name has been defined.

        Returns:
            bool: True if ``first`` (or ``text`` when ``uses_parts`` is False)
                has been set.
        """
        if not self.uses_parts:
            return super().defined()
        return hasattr(self, 'first')

    def familiar(self):
        """Return the familiar (first) name.

        Returns:
            str: First name, or the full name when ``uses_parts`` is False.
        """
        if not self.uses_parts:
            return self.full()
        return self.first

    def full(self, middle='initial', use_suffix=True):  # pylint: disable=arguments-differ
        """Return the full name assembled from its parts.

        Args:
            middle (str, bool, or None): Controls middle-name inclusion.
                ``'initial'`` (default) includes the middle initial;
                ``True`` includes the full middle name; ``False`` or ``None``
                omits it.
            use_suffix (bool): If True (default), append the suffix when
                present.

        Returns:
            str: Full name string.
        """
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
        """Return the name in "First Last" format.

        Returns:
            str: First and last name separated by a space.
        """
        if not self.uses_parts:
            return super().firstlast()
        return self.first + " " + self.last

    def lastfirst(self):
        """Return the name in "Last, First Middle" format.

        Returns:
            str: Last name, comma, first name, and optional middle initial and
                suffix.
        """
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
        """Return the middle initial.

        Args:
            with_period (bool): If True (default), append a period after the
                initial.

        Returns:
            str: Middle initial (e.g. ``'A.'``), or an empty string if there
                is no middle name.
        """
        if len(self.middle.strip()) == 0:
            return ''
        if with_period:
            return self.middle[0].strip() + '.'
        return self.middle[0].strip()


class Address(DAObject):
    """A geographic address with geocoding support.

    Attributes:
        address (str): Street address line (e.g. ``'123 Main St'``).
        unit (str): Unit, apartment, or suite number (optional).
        city (str): City name.
        state (str): State or province code.
        zip (str): ZIP or postal code.
        country (str): ISO 3166-1 alpha-2 country code (optional).
        location (LatitudeLongitude): GPS coordinates for the address.
        city_only (bool): If True, only city-level address fields are used.
        norm (Address): Normalized short-format address returned by the
            geocoder (set after geocoding).
        norm_long (Address): Normalized long-format address returned by the
            geocoder (set after geocoding).
    """
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
        """Return the address as a single line of text.

        Args:
            include_unit (bool): If True (default), include the unit number.
            omit_default_country (bool): If True (default), omit the country
                when it matches the interview's default country.
            language (str or None): Language code for localized unit labels.
            show_country (bool or None): If True, always show the country; if
                False, never show it; if None, apply the ``omit_default_country``
                logic.

        Returns:
            str: Address on a single line.
        """
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
        """Return True if geocoding has been attempted.

        Returns:
            bool: True if geocoding was performed; False otherwise.
        """
        if hasattr(self, '_geocoded'):
            return self._geocoded
        return self.geolocated

    def was_geocoded_successfully(self):
        """Return True if geocoding was performed and succeeded.

        Returns:
            bool: True if geocoding was performed successfully; False
                otherwise.
        """
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
        """Return the raw response data from the geocoding service.

        Returns:
            list or dict: Raw geocoder response data, or an empty list if
                geocoding has not been performed.
        """
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
        """Geocode the address to obtain latitude, longitude, and normalized fields.

        Args:
            address (str or None): If provided, geocode this string instead of
                assembling the address from the object's own fields.
            reset (bool): If True, clear any previous geocoding results before
                geocoding.

        Returns:
            bool: True if geocoding succeeded; False otherwise.
        """
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
            except BaseException as the_err:
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
            except BaseException as err:
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
        """Clear all geocoding results so the address can be geocoded again."""
        self.delattr('norm', 'geolocate_success', 'geolocate_response', '_geocode_success', '_geocode_response', 'norm_long', 'one_line')
        self._geocoded = False
        self.geolocated = False
        self.location.delattr('gathered', 'known', 'latitude', 'longitude', 'description')

    def block(self, language=None, international=False, show_country=None):
        """Return the address formatted as a multi-line mailing block.

        Args:
            language (str or None): Language code for localized labels.
            international (bool): If True, use the i18n-address library for
                country-appropriate formatting.
            show_country (bool or None): If True, always include the country
                line; if False, never include it; if None, include it only
                when the country differs from the interview's default.

        Returns:
            str: Multi-line address block (lines joined with ``[NEWLINE]``
                markers in non-DOCX contexts).
        """
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
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
        """Return the unit number formatted as a display string.

        Args:
            language (str or None): Language code for the ``'Unit'``,
                ``'Floor'``, or ``'Room'`` label.
            require (bool): If True, trigger a question to collect the
                ``unit`` attribute when it is missing.

        Returns:
            str: Formatted unit string (e.g. ``'Unit 3B'``), or an empty
                string if no unit is defined.
        """
        if not hasattr(self, 'unit') and not hasattr(self, 'floor') and not hasattr(self, 'room'):
            if require:
                self.unit  # pylint: disable=pointless-statement
            else:
                return ''
        if hasattr(self, 'unit') and self.unit != '' and self.unit is not None:
            if not re.search(r'apartment|apt|basement|bsmt|building|bldg|department|dept|floor|fl|front|frnt|hanger|hngr|key|lobby|lbby|lot|lower|lowr|office|ofc|penthouse|ph|pier|rear|room|rm|side|slip|space|spc|stop|suite|ste|trailer|trlr|unit|upper|uppr', str(self.unit), flags=re.IGNORECASE):
                return word("Unit", language=language) + " " + str(self.unit)
            return str(self.unit)
        if hasattr(self, 'floor') and self.floor != '' and self.floor is not None:
            return word("Floor", language=language) + " " + str(self.floor)
        if hasattr(self, 'room') and self.room != '' and self.room is not None:
            return word("Room", language=language) + " " + str(self.room)
        return ''

    def line_one(self, language=None):
        """Return the first line of the address.

        Args:
            language (str or None): Language code for the unit label.

        Returns:
            str: Street address and optional unit, or an empty string for
                city-only addresses.
        """
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
        """Return the second line of the address.

        Returns:
            str: City, state, and ZIP/postal code.
        """
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
    """Return ISO 3166-1 country data for a given country name or code.

    Args:
        country (str): Country name or code (fuzzy-matched with
            ``pycountry``).
        part (str): The field to return — ``'alpha_2'`` (default),
            ``'alpha_3'``, ``'name'``, ``'official_name'``, or
            ``'numeric'``.

    Returns:
        str: Requested field value for the matched country.

    Raises:
        DAError: If the country cannot be found or the ``part`` is
            unrecognized.
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
    """An Address whose ``city_only`` flag is set to True from initialization."""

    def init(self, *pargs, **kwargs):
        self.city_only = True
        super().init(*pargs, **kwargs)


class Thing(DAObject):
    """An object that has a name.

    Attributes:
        name (Name): The name of the thing.
    """
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
    """An event with a city-level address and GPS location.

    Attributes:
        address (City): The city where the event takes place.
        location (LatitudeLongitude): GPS coordinates of the event.
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
    """A legal or natural person with a name, address, and location.

    Attributes:
        name (Name): The person's name.
        address (Address): The person's address.
        location (LatitudeLongitude): The person's GPS location.
        email (str): Email address.
        phone_number (str): Phone number.
    """
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
            elif self is docassemble.base.functions.this_thread.global_vars.user:
                result['icon'] = DEFAULT_BLUE_ICON
            return [result]
        return None

    def identified(self):
        """Return True if the person's name has been defined.

        Returns:
            bool: True if the name text has been set; False otherwise.
        """
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
        """Return the objective pronoun for the person.

        Args:
            **kwargs: Optional ``capitalize=True`` to capitalize the result.
                ``person`` overrides the point-of-view (``'1'``, ``'1p'``,
                ``'2'``, ``'2p'``, or ``'3'``).

        Returns:
            str: Objective pronoun (e.g. ``'it'``, ``'you'``, ``'me'``).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.you_objective(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.you_objective_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.me_objective(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.us_objective(**kwargs)
        else:
            output = docassemble.base.functions.it_objective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def object_possessive(self, target, **kwargs):
        """Return a possessive phrase using the variable name.

        Args:
            target (str): The thing being possessed.
            **kwargs: Optional ``capitalize=True`` to capitalize the result.
                ``person`` overrides the point-of-view.

        Returns:
            str: Possessive phrase (e.g. ``'your fish'`` or ``'my fish'``).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            return your(target, **kwargs)
        if person == '2p':
            return docassemble.base.functions.your_plural(target, **kwargs)
        if person == '1':
            return docassemble.base.functions.my_possessive(target, **kwargs)
        if person == '1p':
            return docassemble.base.functions.our_possessive(target, **kwargs)
        return super().object_possessive(target, **kwargs)

    def is_are_you(self, **kwargs):
        """Return "are you" for the user, or "is [name]" for a third party.

        Args:
            **kwargs: Optional ``capitalize=True`` to capitalize the result.
                ``person`` overrides the point-of-view.

        Returns:
            str: Appropriate verb phrase (e.g. ``'are you'`` or ``'is Jane'``).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.are_you(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.are_you_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.am_i(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.are_we(**kwargs)
        else:
            output = is_word(str(self), **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def address_block(self, language=None, international=False, show_country=False):
        """Return the person's name and address formatted as a mailing block.

        Args:
            language (str or None): Language code for localized labels.
            international (bool): If True, use i18n-address formatting.
            show_country (bool): If True, include the country line.

        Returns:
            str: Name followed by the address block.
        """
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return self.name.full() + '</w:t><w:br/><w:t xml:space="preserve">' + self.address.block(language=language, international=international, show_country=show_country)
        return "[FLUSHLEFT] " + self.name.full() + " [NEWLINE] " + self.address.block(language=language, international=international, show_country=show_country)

    def sms_number(self, country=None):
        """Return the person's phone number in E.164 format for SMS.

        Uses ``mobile_number`` if defined, otherwise ``phone_number``.

        Args:
            country (str or None): ISO 3166-1 alpha-2 country code used when
                parsing the number. Defaults to the address country or the
                interview default.

        Returns:
            str or None: E.164-formatted phone number, or None if parsing
                fails.
        """
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

    def subject(self, **kwargs):
        return self.subjective_pronoun_or_name(**kwargs)

    def facsimile_number(self, country=None):
        """Return the person's fax number in E.164 format.

        Args:
            country (str or None): ISO 3166-1 alpha-2 country code used when
                parsing the number. Defaults to the address country or the
                interview default.

        Returns:
            str or None: E.164-formatted fax number, or None if parsing fails.
        """
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
        """Return the person's email address, optionally with display name.

        Args:
            include_name (bool or None): If True, include the name in
                ``"Name" <address>`` format. If None (default), include
                the name when it is defined.

        Returns:
            str: Formatted email address.
        """
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


class Individual(Person):
    """A natural person with a first/last name and biographical attributes.

    Attributes:
        name (IndividualName): The individual's name, stored as parts.
        birthdate (datetime.date or str): Date of birth.
        gender (str): Gender string (e.g. ``'male'``, ``'female'``).
    """
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
        """Return the individual's familiar (first) name.

        Returns:
            str: First name, or full name when ``uses_parts`` is False.
        """
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
        """Return True if the individual's name has been defined.

        Returns:
            bool: True if ``name.first`` has been set; False otherwise.
        """
        if hasattr(self.name, 'first'):
            return True
        return False

    def age_in_years(self, decimals=False, as_of=None):
        """Return the individual's age in years.

        Args:
            decimals (bool): If True, return a float with fractional years;
                otherwise return an integer.
            as_of (datetime.date, str, or None): Calculate age as of this
                date instead of today.

        Returns:
            int or float: Age in years.
        """
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
            return float(rd.years + rd.months/12.0 + rd.days/365.0 + rd.hours/(365.0*24.0) + rd.minutes/(365.0*24.0*60.0))
        return int(rd.years)

    def age_in_months(self, decimals=False, as_of=None):
        """Return the individual's age in months.

        Args:
            decimals (bool): If True, return a float with fractional months;
                otherwise return an integer.
            as_of (datetime.date, str, or None): Calculate age as of this
                date instead of today.

        Returns:
            int or float: Age in months.
        """
        if as_of is None:
            comparator = current_datetime()
        else:
            comparator = as_datetime(as_of)
        birth_date = as_datetime(self.birthdate)
        rd = dateutil.relativedelta.relativedelta(comparator, birth_date)
        if decimals:
            return float(rd.years*12.0 + rd.months + 12.0*(rd.days/365.0 + rd.hours/(365.0*24.0) + rd.minutes/(365.0*24.0*60.0)))
        return int(rd.years*12.0 + rd.months)

    def first_name_hint(self):
        """Return the logged-in user's first name as a hint for the interview.

        Returns:
            str: First name from the user profile when this individual is the
                current user and they are authenticated; otherwise an empty
                string.
        """
        if self is docassemble.base.functions.this_thread.global_vars.user and docassemble.base.functions.this_thread.current_info['user']['is_authenticated'] and 'firstname' in docassemble.base.functions.this_thread.current_info['user'] and docassemble.base.functions.this_thread.current_info['user']['firstname']:
            return docassemble.base.functions.this_thread.current_info['user']['firstname']
        return ''

    def last_name_hint(self):
        """Return the logged-in user's last name as a hint for the interview.

        Returns:
            str: Last name from the user profile when this individual is the
                current user and they are authenticated; otherwise an empty
                string.
        """
        if self is docassemble.base.functions.this_thread.global_vars.user and docassemble.base.functions.this_thread.current_info['user']['is_authenticated'] and 'lastname' in docassemble.base.functions.this_thread.current_info['user'] and docassemble.base.functions.this_thread.current_info['user']['lastname']:
            return docassemble.base.functions.this_thread.current_info['user']['lastname']
        return ''

    def salutation(self, **kwargs):
        """Return the appropriate salutation for the individual.

        Args:
            **kwargs: Forwarded to ``salutation()``; supports ``capitalize``.

        Returns:
            str: Salutation string (e.g. ``'Mr.'``, ``'Ms.'``).
        """
        return salutation(self, **kwargs)

    def pronoun_possessive(self, target, **kwargs):
        """Return a gendered possessive phrase for the individual.

        Args:
            target (str): The thing being possessed (e.g. ``'fish'``).
            **kwargs: Optional ``capitalize=True`` to capitalize the result.
                ``thirdperson=True`` forces third-person regardless of
                point-of-view. ``person`` overrides the point-of-view.

        Returns:
            str: Possessive phrase (e.g. ``'her fish'``, ``'his fish'``,
                ``'your fish'``).
        """
        thirdperson = kwargs.pop('thirdperson', False)
        if thirdperson:
            person = '3'
        else:
            person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = your(target, **kwargs)
        elif person == '2p':
            output = docassemble.base.functions.your_plural(target, **kwargs)
        elif person == '1':
            output = docassemble.base.functions.my_possessive(target, **kwargs)
        elif person == '1p':
            output = docassemble.base.functions.our_possessive(target, **kwargs)
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
        """Return the gendered objective pronoun for the individual.

        Args:
            **kwargs: Optional ``capitalize=True`` to capitalize the result.
                ``person`` overrides the point-of-view.

        Returns:
            str: Objective pronoun (e.g. ``'you'``, ``'her'``, ``'him'``).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.you_objective(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.you_objective_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.me_objective(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.our_objective(**kwargs)
        elif self.gender == 'female':
            output = docassemble.base.functions.her_objective(**kwargs)
        elif self.gender == 'other':
            output = docassemble.base.functions.genderless_objective(**kwargs)
        else:
            output = docassemble.base.functions.him_objective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def pronoun_objective(self, **kwargs):
        """Return the gendered objective pronoun (alias for :meth:`pronoun`).

        Returns:
            str: Objective pronoun.
        """
        return self.pronoun(**kwargs)

    def pronoun_subjective(self, **kwargs):
        """Return the gendered subjective pronoun for the individual.

        Args:
            **kwargs: Optional ``capitalize=True`` to capitalize the result.
                ``thirdperson=True`` forces third-person. ``person`` overrides
                the point-of-view.

        Returns:
            str: Subjective pronoun (e.g. ``'you'``, ``'she'``, ``'he'``).
        """
        thirdperson = kwargs.pop('thirdperson', False)
        if thirdperson:
            person = '3'
        else:
            person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            output = docassemble.base.functions.you_subjective(**kwargs)
        elif person == '2p':
            output = docassemble.base.functions.you_subjective_plural(**kwargs)
        elif person == '1':
            output = docassemble.base.functions.i_subjective(**kwargs)
        elif person == '1p':
            output = docassemble.base.functions.we_subjective(**kwargs)
        elif self.gender == 'female':
            output = docassemble.base.functions.she_subjective(**kwargs)
        elif self.gender == 'other':
            output = docassemble.base.functions.genderless_subjective(**kwargs)
        else:
            output = docassemble.base.functions.he_subjective(**kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def itself(self, **kwargs):
        """Return the appropriate reflexive pronoun for the individual.

        Args:
            **kwargs: Optional ``capitalize=True`` to capitalize the result.
                ``person`` overrides the point-of-view.

        Returns:
            str: Reflexive pronoun (e.g. ``'yourself'``, ``'herself'``,
                ``'himself'``).
        """
        person = str(kwargs.pop('person', self.get_point_of_view()))
        if person == '2':
            return docassemble.base.functions.yourself(**kwargs)
        if person == '2p':
            return docassemble.base.functions.yourselves(**kwargs)
        if person == '1':
            return docassemble.base.functions.myself(**kwargs)
        if person == '1p':
            return docassemble.base.functions.ourselves(**kwargs)
        if self.gender == 'female':
            return docassemble.base.functions.herself(**kwargs)
        if self.gender == 'other':
            return docassemble.base.functions.genderless_self(**kwargs)
        return docassemble.base.functions.himself(**kwargs)

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
    """A list of Individual objects representing children."""
    ChildClass = Individual

    def init(self, *pargs, **kwargs):
        self.object_type = self.ChildClass
        super().init(*pargs, **kwargs)


class Value(DAObject):
    """A monetary value entry in a FinancialList.

    Attributes:
        exists (bool): True if the value is applicable (the item exists).
        value (Decimal or float): The monetary amount.
    """

    def amount(self):
        """Return the value's amount, or 0 if it does not exist.

        Returns:
            Decimal: The amount, or ``Decimal(0)`` when ``exists`` is False.
        """
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
    """A periodic monetary value entry in a PeriodicFinancialList.

    Attributes:
        period (int or float): Number of times per year this value occurs
            (e.g. 12 for monthly, 1 for annual).
        exists (bool): True if the value is applicable.
        value (Decimal or float): The amount per period.
    """

    def amount(self, period_to_use=1):
        """Return the amount normalized to a given period.

        Args:
            period_to_use (int or float): The target period divisor. Use 12
                to get a monthly amount from an annual value, for example.
                Defaults to 1 (returns the raw per-period amount).

        Returns:
            Decimal: Normalized amount, or ``Decimal(0)`` when ``exists`` is
                False.
        """
        if not self.exists:
            return 0
        ensure_definition(period_to_use)
        return (Decimal(self.value) * Decimal(self.period)) / Decimal(period_to_use)


class FinancialList(DADict):
    """A dictionary of Value objects representing a set of currency amounts.

    Attributes:
        elements (dict): Maps item names (str) to Value objects.
    """
    ValueClass = Value

    def init(self, *pargs, **kwargs):
        self.object_type = self.ValueClass
        super().init(*pargs, **kwargs)

    def total(self):
        """Return the total of all existing values in the list.

        Returns:
            Decimal: Sum of the ``value`` amounts for all items where
                ``exists`` is True.
        """
        self._trigger_gather()
        result = 0
        for item in sorted(self.elements.keys()):
            if self[item].exists:
                result += Decimal(self[item].value)
        return result

    def existing_items(self):
        """Return a list of keys for items that exist in the financial list.

        Returns:
            list[str]: Sorted list of item names where ``exists`` is True.
        """
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
    """A FinancialList where each entry has an associated payment period.

    Attributes:
        elements (dict): Maps item names (str) to PeriodicValue objects.
    """
    PeriodicValueClass = PeriodicValue

    def init(self, *pargs, **kwargs):
        self.object_type = self.PeriodicValueClass
        super().init(*pargs, **kwargs)

    def total(self, period_to_use=1):
        """Return the total of all periodic values normalized to a given period.

        Args:
            period_to_use (int or float): The period divisor for normalization.
                Defaults to 1 (returns the sum of ``value * period`` for each
                item).

        Returns:
            Decimal: Normalized total, or 0 if ``period_to_use`` is 0.
        """
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
    """A PeriodicFinancialList for recording a person's income sources."""


class Asset(FinancialList):
    """A FinancialList for recording a person's assets."""


class Expense(PeriodicFinancialList):
    """A PeriodicFinancialList for recording a person's expenses."""


class OfficeList(DAList):
    """A list of Address objects representing offices of an organization."""
    AddressClass = Address

    def init(self, *pargs, **kwargs):
        self.object_type = self.AddressClass
        super().init(*pargs, **kwargs)


class Organization(Person):
    """A company or organization with offices and service areas.

    Attributes:
        office (OfficeList): List of the organization's office addresses.
        handles (list): Types of legal or service problems the organization
            handles.
        serves (list): Counties or geographic areas the organization serves.
    """
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
        """Return True if the organization handles the given problem and/or serves the given county.

        Args:
            problem (str or None): Problem type to check against ``handles``.
            county (str or None): County to check against ``serves``.

        Returns:
            bool: True if all provided criteria are met; False otherwise.
        """
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
    """Return the SMS session information for a phone number.

    Args:
        phone_number (str): Phone number to look up.
        config (str): Twilio configuration name. Defaults to ``'default'``.

    Returns:
        dict or None: Session data dict (without internal keys), or None if no
            session exists for the number.
    """
    result = server.get_sms_session(phone_number, config=config)
    for key in ['number', 'tempuser', 'user_id']:
        if key in result:
            del result[key]
    return result


def initiate_sms_session(phone_number, yaml_filename=None, email=None, new=False, send=True, config='default'):
    """Initiate an SMS session for a phone number.

    Args:
        phone_number (str): Recipient's phone number.
        yaml_filename (str or None): Interview YAML file to start. Defaults to
            the current interview.
        email (str or None): Email address to associate with the SMS user.
        new (bool): If True, always create a new session even if one exists.
        send (bool): If True (default), send an SMS invite immediately.
        config (str): Twilio configuration name. Defaults to ``'default'``.

    Returns:
        bool: True.
    """
    server.initiate_sms_session(phone_number, yaml_filename=yaml_filename, email=email, new=new, config=config)
    if send:
        send_sms_invite(to=phone_number, config=config)
    return True


def terminate_sms_session(phone_number, config='default'):
    """Terminate the SMS session for a phone number.

    Args:
        phone_number (str): Phone number whose session should be ended.
        config (str): Twilio configuration name. Defaults to ``'default'``.

    Returns:
        bool: True if a session was terminated; False otherwise.
    """
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
    """Send an SMS text message via Twilio.

    Args:
        to (str, list, or DAList): Recipient phone number(s).
        body (str or None): Plain-text message body. Required if ``template``
            is not provided.
        template (DATemplate or None): Template whose subject and content
            provide the message body.
        task (str or None): Interview task name to mark as performed on
            successful send.
        task_persistent (bool): If True, the task persists across sessions.
        attachments (list or None): File(s) to attach as MMS media.
        config (str): Twilio configuration name. Defaults to ``'default'``.
        dry_run (bool): If True, do not actually send; only return whether
            sending would succeed.

    Returns:
        bool: True if the message was sent successfully; False otherwise.
    """
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
                    # url = url_start + server.url_for('serve_stored_file', uid=docassemble.base.functions.this_thread.current_info['session'], number=the_attachment.number, filename=the_attachment.filename, extension=the_attachment.extension)
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
                except BaseException as errstr:
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
            return {'FaxStatus': 'not-configured'}
        the_json = server.server_redis.get('da:faxcallback:sid:' + self.sid)
        if the_json is None:
            return {'FaxStatus': 'no-information'}
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
    """Send a fax via Twilio.

    Args:
        fax_number (str or Person): Recipient fax number or a Person object
            with a ``fax_number`` attribute.
        file_object (DAFile, DAFileList, or DAFileCollection): Document to
            fax. Multiple files in a DAFileList are concatenated into a single
            PDF before sending.
        config (str): Twilio configuration name. Defaults to ``'default'``.
        country (str or None): ISO 3166-1 alpha-2 country code for parsing
            the fax number.

    Returns:
        FaxStatus: Object representing the fax send operation.
    """
    if isinstance(file_object, DAFileCollection):
        file_object = file_object._first_file()
    if isinstance(file_object, DAFileList):
        if len(file_object.elements) == 0:
            raise DAError("send_fax: if passing a DAFileList, the DAFileList must have at least one element")
        if len(file_object.elements) == 1:
            file_object = file_object.elements[0]
        else:
            file_object = pdf_concatenate(file_object)
    return FaxStatus(server.send_fax(fax_string(fax_number, country=country), file_object, config, country=country))


def send_email(to=None, sender=None, reply_to=None, cc=None, bcc=None, body=None, html=None, subject="", template=None, task=None, task_persistent=False, attachments=None, mailgun_variables=None, dry_run=False, config=None):
    """Send an email message.

    Args:
        to (str, Person, DAEmailRecipient, list, or DAList): Primary
            recipient(s). Required.
        sender (str, Person, or DAEmailRecipient or None): Sender address.
            Defaults to the interview's configured sender.
        reply_to (str, Person, or DAEmailRecipient or None): Reply-to address.
        cc (str, Person, list, or None): Carbon-copy recipient(s).
        bcc (str, Person, list, or None): Blind carbon-copy recipient(s).
        body (str or None): Plain-text body. If omitted and ``template`` is
            provided, it is derived from the template.
        html (str or None): HTML body. If omitted, it is built from ``body``
            or ``template``.
        subject (str): Subject line. Defaults to the template subject if a
            ``template`` is provided.
        template (DATemplate or None): Template providing subject, body, and
            HTML.
        task (str or None): Interview task name to mark as performed on
            successful send.
        task_persistent (bool): If True, the task persists across sessions.
        attachments (list or None): File(s) to attach. Each item may be a
            DAFile, DAFileList, DAFileCollection, DAStaticFile, or a static
            file reference string.
        mailgun_variables (dict or None): Custom Mailgun variables to include
            in the X-Mailgun-Variables header.
        dry_run (bool): If True, do not send; only check whether sending would
            succeed.
        config (str or None): Email configuration name. Defaults to the
            interview's ``email config`` metadata or ``'default'``.

    Returns:
        bool: True if the email was sent (or would be sent in dry_run mode);
            False otherwise.
    """
    if config is None:
        config = docassemble.base.functions.this_thread.interview.consolidated_metadata.get('email config', None)
    if not config:
        config = 'default'
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
    # logmessage("Sending mail to: " + repr({'subject': subject, 'recipients': to_string, 'sender': sender_string, 'cc': cc_string, 'bcc': bcc_string, 'body': body, 'html': html}))
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
            server.send_mail(msg, config=config)
            logmessage("send_email: finished sending")
        except BaseException as errmess:
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
    """Return markup that embeds a Google Map of the given objects.

    Args:
        *pargs: DAObject instances (or lists thereof) that implement
            ``_map_info()`` — typically Address or Person objects.
        **kwargs: Optional ``center`` keyword argument specifying the object
            to center the map on.

    Returns:
        str: A ``[MAP ...]`` markup string that the interview renderer converts
            to an embedded Google Map, or a localized ``'(Unable to display
            map)'`` string if no map data is available.
    """
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
    """Start OCR on image or PDF files as a background Celery task.

    Args:
        *pargs: First positional argument is the file or list of files to OCR
            (DAFile or DAFileList). An optional second positional argument is a
            UI notification identifier.
        **kwargs: Optional keyword arguments including ``language``,
            ``psm``, ``f``, ``l``, ``x``, ``y``, ``W``, ``H``,
            ``use_google`` (bool), ``raw_result`` (bool), and ``message``.

    Returns:
        celery.result.AsyncResult: A Celery task result object. Call
            ``.get()`` to wait for the result.
    """
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
        args = {'yaml_filename': docassemble.base.functions.this_thread.current_info['yaml_filename'], 'user': docassemble.base.functions.this_thread.current_info['user'], 'user_code': docassemble.base.functions.this_thread.current_info['session'], 'secret': docassemble.base.functions.this_thread.current_info['secret'], 'url': docassemble.base.functions.this_thread.current_info['url'], 'url_root': docassemble.base.functions.this_thread.current_info['url_root'], 'language': language, 'f': arg_f, 'l': arg_l, 'psm': arg_psm, 'x': arg_x, 'y': arg_y, 'W': arg_W, 'H': arg_H, 'extra': ui_notification, 'message': the_message, 'pdf': False, 'preserve_color': False}
        collector = server.ocr_finalize.s(**args)
        todo = []
        indexno = 0
        for item in ocr_page_tasks(image_file, **args):
            todo.append(server.ocr_page.s(indexno, **item))
            indexno += 1
        the_task = server.chord(todo)(collector)  # pylint: disable=assignment-from-none
    if ui_notification is not None:
        worker_key = 'da:worker:uid:' + str(docassemble.base.functions.this_thread.current_info['session']) + ':i:' + str(docassemble.base.functions.this_thread.current_info['yaml_filename']) + ':userid:' + str(docassemble.base.functions.this_thread.current_info['user']['the_user_id'])
        # logmessage("worker_caller: id is " + str(result.obj.id) + " and key is " + worker_key)
        server.server_redis.rpush(worker_key, the_task.id)
    # logmessage("ocr_file_in_background finished")
    return the_task

# def ocr_file_in_background(image_file, ui_notification=None, language=None, psm=6, x=None, y=None, W=None, H=None):
#     """Starts optical character recognition on one or more image files or PDF
#     files and returns an object representing the background task created."""
#     logmessage("ocr_file_in_background: started")
#     return server.async_ocr(image_file, ui_notification=ui_notification, language=language, psm=psm, x=x, y=y, W=W, H=H, user_code=docassemble.base.functions.this_thread.current_info.get('session', None))


def get_work_bucket():
    bucket_name = server.daconfig['google'].get('work bucket', None)
    if bucket_name is None:
        raise DAError("Cannot use Google Storage unless there is a work bucket configured in the google configuration")
    api = DAGoogleAPI()
    client = api.google_cloud_storage_client()
    try:
        bucket = client.get_bucket(bucket_name)
    except:
        try:
            bucket = client.create_bucket(bucket_name)
        except BaseException as err:
            raise DAError("failed to create bucket named " + bucket_name + ": " + str(err))
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
                            if 'fullTextAnnotation' in item and 'text' in item['fullTextAnnotation']:
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
                    raise DAError("Failed to OCR file with Google Cloud Vision: " + the_response.error.message)
                if raw_result:
                    output.append(json.loads(google.cloud.vision.AnnotateImageResponse.to_json(the_response)))
                else:
                    for text in the_response.text_annotations:
                        output += text.description + "\n"
    return output


def ocr_file(image_file, language=None, psm=6, f=None, l=None, x=None, y=None, W=None, H=None, use_google=False, raw_result=False):  # noqa: E741
    """Run optical character recognition on image or PDF files and return the text.

    Args:
        image_file (DAFile or DAFileList): File(s) to OCR.
        language (str or None): Tesseract language code (e.g. ``'eng'``).
            Defaults to the interview language.
        psm (int): Tesseract page segmentation mode. Defaults to 6.
        f (int or None): First page to OCR (PDF only).
        l (int or None): Last page to OCR (PDF only).
        x (int or None): Left edge of the crop rectangle in pixels.
        y (int or None): Top edge of the crop rectangle in pixels.
        W (int or None): Width of the crop rectangle in pixels.
        H (int or None): Height of the crop rectangle in pixels.
        use_google (bool): If True, use Google Cloud Vision instead of
            Tesseract.
        raw_result (bool): If True and ``use_google`` is True, return the
            raw Vision API JSON response.

    Returns:
        str: Recognized text, or a localized error message.

    Raises:
        DAError: If Tesseract or Google Cloud Vision fails.
    """
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
    ocr_resolution = str(int(float(ocr_resolution)*11.0))
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
                args = [pdf_to_ppm, '-scale-to', str(ocr_resolution)]
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
                    result = subprocess.run(args, timeout=3600, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
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
        file_to_read = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".png")
        final_image.save(file_to_read, "PNG")
        file_to_read.seek(0)
        if TESSERACT_MODE == LOCAL:
            try:
                text = subprocess.check_output([TESSERACT_PATH, 'stdin', 'stdout', '-l', str(lang), '--psm', str(psm)], stdin=file_to_read).decode('utf-8', 'ignore')
            except subprocess.CalledProcessError as err:
                raise DAError("ocr_file: failed to OCR file: " + str(err) + " " + str(err.output.decode()))
        elif TESSERACT_MODE == REMOTE:
            result = run_tesseract.delay(['stdin', 'stdout', '-l', str(lang), '--psm', str(psm)], mode=0, file_path=file_to_read.name).get(disable_sync_subtasks=False)  # pylint: disable=possibly-used-before-assignment
            if not result.ok:
                raise DAError("ocr_file: failed to OCR file")
            text = result.content
        else:
            raise DAError("ocr_file: tesseract not installed")
        page_text.append(text)
    for directory in temp_directory_list:
        shutil.rmtree(directory)
    return "\f".join(page_text)


def read_qr(image_file, f=None, l=None, x=None, y=None, W=None, H=None):  # noqa: E741
    """Decode QR codes found in image or PDF files.

    Args:
        image_file (DAFile or DAFileList): File(s) to scan for QR codes.
        f (int or None): First page to scan (PDF only).
        l (int or None): Last page to scan (PDF only).
        x (int or None): Left edge of the crop rectangle in pixels.
        y (int or None): Top edge of the crop rectangle in pixels.
        W (int or None): Width of the crop rectangle in pixels.
        H (int or None): Height of the crop rectangle in pixels.

    Returns:
        list[str]: Decoded QR code data strings, in scan order.
    """
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
    ocr_resolution = str(int(float(ocr_resolution)*11.0))
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
                args = [pdf_to_ppm, '-scale-to', str(ocr_resolution)]
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
                    result = subprocess.run(args, timeout=3600, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
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
    """Return the filesystem path and MIME type of a file.

    Args:
        file_ref (DAFile, DAFileList, DAFileCollection, DAStaticFile, or int):
            Reference to the file.

    Returns:
        tuple[str, str]: ``(path, mimetype)`` — absolute filesystem path and
            MIME type string.
    """
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
    file_info = server.file_finder(file_ref, return_nonexistent=True)
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
    """Concatenate DOCX files into a single DOCX file.

    Args:
        *pargs: DAFile, DAFileList, DAStaticFile, or path strings to
            concatenate.
        **kwargs: Optional keyword arguments:
            - ``output_to`` (DAFile or None): Target file to write into.
            - ``filename`` (str): Filename for the resulting file. Defaults
              to ``'file.docx'``.

    Returns:
        DAFile: The concatenated DOCX file.

    Raises:
        DAError: If no valid files are provided, or ``output_to`` is not a
            DAFile.
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
        raise DAError("docx_concatenate: output_to must be a DAFile")
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


def get_passwords(password):
    if password is None:
        return (None, None)
    if isinstance(password, (str, bool, int, float)):
        owner_password = None
        user_password = str(password).strip()
    elif isinstance(password, list) and len(password) == 1:
        owner_password = password[0]
        user_password = None
    elif isinstance(password, list) and len(password) >= 2:
        owner_password = password[0]
        user_password = password[1]
    elif isinstance(password, dict):
        owner_password = password.get('owner', None)
        user_password = password.get('user', None)
    else:
        raise DAError("get_passwords: invalid password")
    if isinstance(owner_password, (str, bool, int, float)):
        owner_password = str(owner_password).strip()
    if isinstance(user_password, (str, bool, int, float)):
        user_password = str(user_password).strip()
    return (owner_password, user_password)


def pdf_concatenate(*pargs, **kwargs):
    """Concatenate PDF files into a single PDF file.

    Args:
        *pargs: DAFile, DAFileList, DAFileCollection, DAStaticFile, or path
            strings representing the PDF files to concatenate.
        **kwargs: Optional keyword arguments:
            - ``output_to`` (DAFile or None): Target file to write into.
            - ``filename`` (str): Filename for the resulting file. Defaults
              to ``'file.pdf'``.
            - ``pdfa`` (bool): If True, convert to PDF/A.
            - ``password`` (str, list, or dict): Password(s) to apply to the
              output PDF.

    Returns:
        DAFile: The concatenated PDF file.

    Raises:
        DAError: If no valid files are provided, or ``output_to`` is not a
            DAFile.
    """
    paths = []
    get_pdf_paths(list(pargs), paths)
    if len(paths) == 0:
        raise DAError("pdf_concatenate: no valid files to concatenate")
    (owner_password, password) = get_passwords(kwargs.get('password', None))
    pdf_path = docassemble.base.pandoc.concatenate_files(paths, pdfa=kwargs.get('pdfa', False), password=password, owner_password=owner_password)
    pdf_file = kwargs.get('output_to', None)
    if pdf_file is None:
        pdf_file = DAFile()
        pdf_file.set_random_instance_name()
    elif isinstance(pdf_file, DAFileList):
        pdf_file = pdf_file.elements[0]
    if not isinstance(pdf_file, DAFile):
        raise DAError("pdf_concatenate: output_to must be a DAFile")
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
    """Create a ZIP archive from the provided files and return it as a DAFile.

    Args:
        *pargs: Files to include. Each argument may be a DAFile, DAFileList,
            DAFileCollection, DAStaticFile, or a dict mapping folder names to
            files.
        **kwargs: Optional keyword arguments:
            - ``output_to`` (DAFile or None): Target DAFile to write into.
            - ``filename`` (str): Filename for the ZIP archive. Defaults to
              ``'file.zip'``.

    Returns:
        DAFile: The ZIP archive file.
    """
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
        raise DAError("zip_file: output_to must be a DAFile")
    the_zip_file.initialize(filename=kwargs.get('filename', 'file.zip'), reinitialize=the_zip_file.ok)
    zf = zipfile.ZipFile(the_zip_file.path(), compression=zipfile.ZIP_DEFLATED, mode='w')
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
        info.date_time = datetime.datetime.fromtimestamp(os.path.getmtime(path), datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)).timetuple()
        with open(path, 'rb') as fp:
            zf.writestr(info, fp.read())
    zf.close()
    the_zip_file.retrieve()
    the_zip_file.commit()
    return the_zip_file


def validation_error(the_message, field=None):
    """Raise a validation error to reject a field value in the interview.

    Args:
        the_message (str): Human-readable message to display to the user.
        field (str or None): Field variable name to associate the error with.
            If None, the error applies to the entire question.

    Raises:
        DAValidationError: Always raised with the given message and field.
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
    """Return a URL that, when visited, seeks a sequence of variables.

    Similar to ``url_action``, but accepts a structured list describing which
    variables to seek, undefine, invalidate, recompute, or set.

    Args:
        data (str, dict, or list): A variable name, a control dict (with
            ``'undefine'``, ``'invalidate'``, ``'recompute'``, ``'set'``, or
            ``'follow up'`` keys), an action dict (with ``'action'`` and
            ``'arguments'`` keys), or a list combining any of the above.

    Returns:
        str: URL that drives the interview to seek the requested variables.

    Raises:
        DAError: If variable names are invalid or the data structure is
            malformed.
    """
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
                variables.append({'action': '_da_set', 'arguments': {'variables': clean_list}})
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
                    variables.append({'action': var, 'arguments': {}})
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
                    variables.append({'action': '_da_invalidate', 'arguments': {'variables': clean_list}})
                else:
                    variables.append({'action': '_da_undefine', 'arguments': {'variables': clean_list}})
                if the_command == 'recompute':
                    variables.append({'action': '_da_compute', 'arguments': {'variables': clean_list}})
            continue
        if isinstance(the_saveas, dict) and len(the_saveas) == 2 and 'action' in the_saveas and 'arguments' in the_saveas:
            if not isinstance(the_saveas['arguments'], dict):
                raise DAError("url_ask: an arguments directive must refer to a dictionary.  " + repr(data))
            if contains_volatile.search(the_saveas['action']):
                raise DAError("url_ask cannot be used with a generic object or a variable iterator")
            variables.append({'action': the_saveas['action'], 'arguments': the_saveas['arguments']})
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
    """Return HTML for a Bootstrap button that links to a URL.

    Args:
        url (str): The URL the button navigates to.
        icon (str or None): Font Awesome icon name (e.g. ``'pencil'``).
        color (str): Bootstrap color variant (e.g. ``'success'``,
            ``'danger'``, ``'primary'``). Defaults to ``'success'``.
        size (str): Bootstrap button size — ``'sm'``, ``'md'``, or ``'lg'``.
            Defaults to ``'sm'``.
        block (bool): If True, make the button full-width. Defaults to False.
        label (str): Button label text. Defaults to ``'Edit'``.
        classname (str or None): Additional CSS class(es) to add to the button.
        new_window (bool, str, or None): If True, open in a new tab/window;
            if a string, use it as the ``target`` attribute value.
        id_tag (str or None): HTML ``id`` attribute for the button.

    Returns:
        str: HTML ``<a>`` element styled as a Bootstrap button.
    """
    if not isinstance(label, str):
        label = 'Edit'
    if color not in ('primary', 'secondary', 'tertiary', 'success', 'danger', 'warning', 'info', 'light', 'dark', 'link'):
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
            icon = 'fa-solid fa-' + icon
        icon = re.sub(r'^fas ', 'fa-solid ', icon)
        icon = re.sub(r'^far ', 'fa-regular ', icon)
        icon = re.sub(r'^fab ', 'fa-brands ', icon)
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
    """Overlay pages from one PDF on top of the pages of another PDF.

    Args:
        main_pdf (DAFile, DAFileCollection, DAFileList, or str): The base PDF.
        logo_pdf (DAFile, DAFileCollection, DAFileList, or str): The PDF whose
            pages are stamped on top of ``main_pdf``.
        first_page (int or None): First page of ``main_pdf`` to stamp.
        last_page (int or None): Last page of ``main_pdf`` to stamp.
        logo_page (int or None): Page from ``logo_pdf`` to use as the stamp.
        only (int or None): Single page of ``main_pdf`` to stamp.
        multi (bool): If True, cycle through all pages of ``logo_pdf`` when
            stamping.
        output_to (DAFile or None): Target DAFile for the result. A new
            DAFile is created if None.
        filename (str or None): Filename for the output file. Defaults to
            ``'file.pdf'``.

    Returns:
        DAFile: The stamped PDF file.

    Raises:
        DAError: If the PDF references are invalid or ``output_to`` is not a
            DAFile.
    """
    if isinstance(main_pdf, DAFileCollection):
        main_file = main_pdf.pdf.path()
    elif isinstance(main_pdf, (DAFile, DAStaticFile, DAFileList)):
        main_file = main_pdf.path()
    elif isinstance(main_pdf, str):
        main_file = main_pdf
    else:
        raise DAError("overlay_pdf: bad main filename")
    if isinstance(logo_pdf, DAFileCollection):
        logo_file = logo_pdf.pdf.path()
    elif isinstance(logo_pdf, (DAFile, DAStaticFile, DAFileList)):
        logo_file = logo_pdf.path()
    elif isinstance(logo_pdf, str):
        logo_file = logo_pdf
    else:
        raise DAError("overlay_pdf: bad logo filename")
    outfile = output_to
    if outfile is None:
        outfile = DAFile()
        outfile.set_random_instance_name()
    elif isinstance(outfile, DAFileList):
        outfile = outfile.elements[0]
    if not isinstance(outfile, DAFile):
        raise DAError("overlay_pdf: output_to must be a DAFile")
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
    """Add an explanation string to the session's explanation history.

    Args:
        the_explanation (str): The explanation text to record.
        category (str): Category name for grouping explanations. Defaults to
            ``'default'``.
    """
    if 'explanations' not in docassemble.base.functions.this_thread.internal:
        docassemble.base.functions.this_thread.internal['explanations'] = {}
    if category not in docassemble.base.functions.this_thread.internal['explanations']:
        docassemble.base.functions.this_thread.internal['explanations'][category] = []
    if the_explanation not in docassemble.base.functions.this_thread.internal['explanations'][category]:
        docassemble.base.functions.this_thread.internal['explanations'][category].append(the_explanation)


def clear_explanations(category='default'):
    """Clear the session's explanation history.

    Args:
        category (str): Category to clear, or ``'all'`` to clear every
            category. Defaults to ``'default'``.
    """
    if 'explanations' not in docassemble.base.functions.this_thread.internal:
        return
    if category == 'all':
        docassemble.base.functions.this_thread.internal['explanations'] = {}
    if category not in docassemble.base.functions.this_thread.internal['explanations']:
        return
    docassemble.base.functions.this_thread.internal['explanations'][category] = []


def logic_explanation(category='default'):
    """Return the list of recorded explanations for a category.

    Args:
        category (str): Category name. Defaults to ``'default'``.

    Returns:
        list[str]: Explanation strings recorded for the category, in order.
    """
    if 'explanations' not in docassemble.base.functions.this_thread.internal:
        return []
    return docassemble.base.functions.this_thread.internal['explanations'].get(category, [])


def set_status(**kwargs):
    """Set miscellaneous key-value status settings for the interview session.

    Args:
        **kwargs: Arbitrary key-value pairs to store in the session's internal
            ``'misc'`` dictionary.
    """
    if 'misc' not in docassemble.base.functions.this_thread.internal:
        docassemble.base.functions.this_thread.internal['misc'] = {}
    for key, val in kwargs.items():
        docassemble.base.functions.this_thread.internal['misc'][key] = val


def get_status(setting):
    """Retrieve a miscellaneous status setting for the interview session.

    Args:
        setting (str): The key to look up.

    Returns:
        object or None: The stored value, or None if the key does not exist.
    """
    if 'misc' not in docassemble.base.functions.this_thread.internal:
        return None
    return docassemble.base.functions.this_thread.internal['misc'].get(setting, None)


def prevent_dependency_satisfaction(f):

    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (NameError, AttributeError, DAIndexError, UndefinedError):
            raise DAError("Reference to undefined variable in context where dependency satisfaction not allowed")
    return wrapper


def assemble_docx(input_file, fields=None, output_path=None, output_format='docx', return_content=False, pdf_options=None, filename=None):
    """Render a DOCX template file and return or save the result.

    Args:
        input_file (DAFile, DAStaticFile, or str): The DOCX template file.
        fields (dict or None): Extra variables to pass to the Jinja2 template.
            Defaults to the current interview's variable dictionary.
        output_path (str or None): Filesystem path to write the output.
            If None, a temporary file is used.
        output_format (str): ``'docx'``, ``'pdf'``, or ``'md'``. Defaults to
            ``'docx'``.
        return_content (bool): If True, return the file contents as bytes
            (or str for ``'md'``) instead of a path. Defaults to False.
        pdf_options (dict or None): PDF conversion options when
            ``output_format`` is ``'pdf'`` (keys: ``pdfa``, ``password``,
            ``owner_password``, ``update_refs``, ``tagged``).
        filename (str or None): Filename hint passed to the PDF converter.

    Returns:
        str or bytes or None: File path (str) when a temporary file is used
            and ``return_content`` is False; file contents (bytes or str)
            when ``return_content`` is True; None when ``output_path`` is
            specified.

    Raises:
        DAError: If the input file is missing, the format is invalid, or
            conversion fails.
    """
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
        docassemble.base.file_docx.fix_docx(output_path)
    elif output_format == 'pdf':
        temp_file = tempfile.NamedTemporaryFile()
        docx_template.save(temp_file.name)
        docassemble.base.file_docx.fix_docx(temp_file.name)
        if not isinstance(pdf_options, dict):
            pdf_options = {}
        result = docassemble.base.pandoc.word_to_pdf(temp_file.name, 'docx', output_path, pdfa=pdf_options.get('pdfa', False), password=pdf_options.get('password', None), owner_password=pdf_options.get('owner_password', None), update_refs=pdf_options.get('update_refs', False), tagged=pdf_options.get('tagged', False), filename=filename)
        if not result:
            raise DAError("Error converting to PDF")
    elif output_format == 'md':
        temp_file = tempfile.NamedTemporaryFile()
        docx_template.save(temp_file.name)
        docassemble.base.file_docx.fix_docx(temp_file.name)
        if can_convert_word_to_markdown():
            result = docassemble.base.pandoc.word_to_markdown(temp_file.name, 'docx')
        else:
            result = None
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


def variables_snapshot_connect():
    return server.variables_snapshot_connect()


def get_persistent_task_store(persistent):
    if persistent is True:
        base = 'session'
    else:
        base = persistent
    if base == 'session':
        encrypted = docassemble.base.functions.this_thread.current_info.get('encrypted', True)
        store = DAStore('store', base=base, encrypted=encrypted)
    else:
        store = DAStore('store', base=base)
    if not store.defined('tasks'):
        store.set('tasks', {})
    return store


def task_performed(task, persistent=False):
    """Return True if the given task has been performed at least once.

    Args:
        task (str): Task name to check.
        persistent (bool or str): If True or a scope string, check the
            persistent task store instead of the session. Defaults to False.

    Returns:
        bool: True if the task counter is greater than zero; False otherwise.
    """
    ensure_definition(task)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        if task in tasks and tasks[task]:  # pylint: disable=unsubscriptable-object,unsupported-membership-test
            return True
        return False
    if task in docassemble.base.functions.this_thread.internal['tasks'] and docassemble.base.functions.this_thread.internal['tasks'][task]:
        return True
    return False


def task_not_yet_performed(task, persistent=False):
    """Return True if the given task has never been performed.

    Args:
        task (str): Task name to check.
        persistent (bool or str): If True or a scope string, check the
            persistent task store. Defaults to False.

    Returns:
        bool: True if the task has not been performed; False otherwise.
    """
    ensure_definition(task)
    if task_performed(task, persistent=persistent):
        return False
    return True


def mark_task_as_performed(task, persistent=False):
    """Increment the task counter by 1.

    Args:
        task (str): Task name to mark.
        persistent (bool or str): If True or a scope string, update the
            persistent task store. Defaults to False.

    Returns:
        int: Updated task counter value.
    """
    ensure_definition(task)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        if task not in tasks:  # pylint: disable=unsupported-membership-test
            tasks[task] = 0  # pylint: disable=unsupported-assignment-operation
        tasks[task] += 1  # pylint: disable=unsupported-assignment-operation
        store.set('tasks', tasks)
        return tasks[task]  # pylint: disable=unsubscriptable-object
    if task not in docassemble.base.functions.this_thread.internal['tasks']:
        docassemble.base.functions.this_thread.internal['tasks'][task] = 0
    docassemble.base.functions.this_thread.internal['tasks'][task] += 1
    return docassemble.base.functions.this_thread.internal['tasks'][task]


def times_task_performed(task, persistent=False):
    """Return the number of times the task has been performed.

    Args:
        task (str): Task name to query.
        persistent (bool or str): If True or a scope string, query the
            persistent task store. Defaults to False.

    Returns:
        int: Number of times the task has been performed (0 if never).
    """
    ensure_definition(task)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        if task not in tasks:  # pylint: disable=unsupported-membership-test
            return 0
        return tasks[task]  # pylint: disable=unsubscriptable-object
    if task not in docassemble.base.functions.this_thread.internal['tasks']:
        return 0
    return docassemble.base.functions.this_thread.internal['tasks'][task]


def set_task_counter(task, times, persistent=False):
    """Set the task counter to a specific value.

    Args:
        task (str): Task name to update.
        times (int): Value to set the counter to.
        persistent (bool or str): If True or a scope string, update the
            persistent task store. Defaults to False.
    """
    ensure_definition(task, times)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        tasks[task] = times  # pylint: disable=unsupported-assignment-operation
        store.set('tasks', tasks)
        return
    docassemble.base.functions.this_thread.internal['tasks'][task] = times


def stash_data(data, expire=None):
    """Store data in encrypted form and return a retrieval key and secret.

    Args:
        data (object): Picklable Python object to stash.
        expire (int or None): TTL in seconds. Defaults to 90 days.

    Returns:
        tuple[str, str]: ``(stash_key, secret)`` — pass both to
            :func:`retrieve_stashed_data` to recover the data.

    Raises:
        DAError: If ``expire`` is not a positive integer.
    """
    if expire is None:
        expire = 60*60*24*90
    try:
        expire = int(expire)
        assert expire > 0
    except:
        raise DAError("Invalid expire value")
    return server.stash_data(data, expire)


def retrieve_stashed_data(stash_key, secret, delete=False, refresh=False):
    """Retrieve data previously stored with :func:`stash_data`.

    Args:
        stash_key (str): Key returned by :func:`stash_data`.
        secret (str): Decryption secret returned by :func:`stash_data`.
        delete (bool): If True, delete the stash after retrieval. Defaults to
            False.
        refresh (bool or int): If True, reset the TTL to 90 days. If a
            positive integer, reset the TTL to that many seconds.

    Returns:
        object: The original stashed Python object, or None if not found.
    """
    if refresh and not (isinstance(refresh, int) and refresh > 0):
        refresh = 60*60*24*90
    return server.retrieve_stashed_data(stash_key, secret, delete=delete, refresh=refresh)


class DABreadCrumbs(DAObject):
    """A breadcrumb navigation widget for multi-step interviews."""

    def get_crumbs(self):
        """Return the breadcrumb trail for the current interview action stack.

        Returns:
            list[dict]: List of dicts with ``'breadcrumb'`` keys, representing
                parent questions followed by the current question.
        """
        return docassemble.base.functions.get_action_stack()

    def show(self):
        """Return HTML for the breadcrumb navigation element.

        Returns:
            str: HTML ``<nav>`` breadcrumb element, or an empty string if
                there are fewer than two crumbs.
        """
        crumbs = self.get_crumbs()
        if len(crumbs) < 2:
            return ''
        last_indexno = len(crumbs) - 1
        return self.container(self.inner(item['breadcrumb'], indexno == last_indexno) for indexno, item in enumerate(crumbs))

    def container(self, items):
        """Return the HTML container wrapping the breadcrumb items.

        Args:
            items (iterable[str]): HTML strings for each breadcrumb item.

        Returns:
            str: HTML ``<nav>`` element containing an ordered list.
        """
        return '<nav class="da-breadcrumb mt-2" aria-label="' + word('breadcrumb') + '"><ol class="breadcrumb">' + ''.join(items) + '</ol></nav>\n'

    def inner(self, label, active):
        """Return the HTML for a single breadcrumb item.

        Args:
            label (str): Display label for the breadcrumb.
            active (bool): If True, mark the item as the current (active)
                page.

        Returns:
            str: HTML ``<li>`` element for the breadcrumb.
        """
        if active:
            return '<li class="da-breadcrumb-item breadcrumb-item">' + label + '</li>'
        return '<li class="da-breadcrumb-item breadcrumb-item active" aria-current="page">' + label + '</li>'


def safeid(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf-8'), 'base64').decode())


def _extract_id_token(id_token):
    if isinstance(id_token, bytes):
        segments = id_token.split(b'.')
    else:
        segments = id_token.split('.')

    if len(segments) != 3:
        raise DAException('Wrong number of segments in token: {0}'.format(id_token))

    if isinstance(segments[1], str):
        b64string = segments[1].encode('ascii')
    else:
        b64string = segments[1]
    if not isinstance(b64string, bytes):
        raise ValueError('{0!r} could not be converted to bytes'.format(value))

    return json.loads(base64.urlsafe_b64decode(b64string + b'=' * (4 - len(b64string) % 4)).decode('utf-8'))


class DAOAuth(DAObject):
    """A base class for performing OAuth2 authorization flows within an interview.

    Attributes:
        url_args (dict): URL query parameters received from the OAuth2
            callback (must be passed as a keyword argument at construction).
    """

    def init(self, *pargs, **kwargs):
        if 'url_args' not in kwargs:
            raise DAError("DAOAuth: you must pass the url_args as a keyword parameter")
        self.url_args = kwargs['url_args']
        del kwargs['url_args']
        super().init(*pargs, **kwargs)

    def _get_flow(self):
        app_credentials = get_config('oauth', {}).get(self.appname, {})
        client_id = app_credentials.get('id', None)
        client_secret = app_credentials.get('secret', None)
        if client_id is None or client_secret is None:
            raise DAError('The application ' + self.appname + " is not configured in the Configuration")
        return OAuth2Session(client_id,
                             redirect_uri=re.sub(r'\?.*', '', interview_url()),
                             scope=self.scope)

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
        raise DAError("DAOAuth: unable to set a random unique id")

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
                app_credentials = get_config('oauth', {}).get(self.appname, {})
                client_id = app_credentials.get('id', None)
                client_secret = app_credentials.get('secret', None)
                r.delete(r_key)
                if self.url_args['state'] != stored_state.decode():
                    raise DAError("State did not match.  " + repr(self.url_args['state']) + " vs " + repr(stored_state.decode()) + " where r_key is " + repr(r_key))
                flow = self._get_flow()
                token_dict = flow.fetch_token(
                    self.token_uri,
                    code=self.url_args['code'],
                    client_secret=client_secret)
                if hasattr(self, 'user_agent') and self.user_agent:
                    user_agent = self.user_agent
                else:
                    user_agent = 'Python client library'
                if token_dict.get('refresh_token'):
                    refresh_token = token_dict['refresh_token']
                elif hasattr(self, 'refresh_token') and self.refresh_token:
                    refresh_token = self.refresh_token
                else:
                    refresh_token = None
                if hasattr(self, 'token_info_uri') and self.token_info_uri:
                    token_info_uri = self.token_info_uri
                else:
                    token_info_uri = None
                if hasattr(self, 'revoke_uri') and self.revoke_uri:
                    revoke_uri = self.revoke_uri
                else:
                    revoke_uri = None
                if 'expires_in' in token_dict:
                    delta = datetime.timedelta(seconds=int(token_dict['expires_in']))
                    token_expiry = delta + datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                else:
                    token_expiry = None
                extracted_id_token = None
                id_token_jwt = None
                if 'id_token' in token_dict:
                    extracted_id_token = _extract_id_token(token_dict['id_token'])
                    id_token_jwt = token_dict['id_token']
                credentials = oauth2client.client.OAuth2Credentials(
                    token_dict['access_token'], client_id, client_secret,
                    refresh_token, token_expiry, self.token_uri, user_agent,
                    revoke_uri=revoke_uri, id_token=extracted_id_token,
                    id_token_jwt=id_token_jwt, token_response=token_dict, scopes=self.scope,
                    token_info_uri=token_info_uri)
                storage = self._get_redis_cred_storage()
                storage.put(credentials)
                del self.url_args['code']
                del self.url_args['state']
            else:
                message("Please wait.", "You are in the process of authenticating.", dead_end=True)
        storage = self._get_redis_cred_storage()
        credentials = storage.get()
        if not credentials or credentials.invalid:
            flow = self._get_flow()
            uri, state_string = flow.authorization_url(self.auth_uri, access_type='offline', prompt='consent')
            pipe = r.pipeline()
            pipe.set(r_key, state_string)
            pipe.expire(r_key, 300)
            pipe.execute()
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
                    if item.__class__.__name__ == 'ReturnValue':
                        if isinstance(item.value, dict):
                            if 'page' in item.value:
                                file_list.append([item.value['indexno'], int(item.value['page']), item.value['doc']._pdf_page_path(int(item.value['page']))])
                            else:
                                file_list.append([item.value['indexno'], 0, item.value['doc'].path()])
            else:
                if parg.__class__.__name__ == 'ReturnValue':
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
                if item.__class__.__name__ == 'ReturnValue' and isinstance(item.value, dict):
                    output[int(item.value['page'])] = item.value['text']
        else:
            if parg.__class__.__name__ == 'ReturnValue' and isinstance(parg.value, dict):
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
                    raise DAError("could not get OCR language for language " + str(language) + "; using language " + str(lang))
            except BaseException as the_error:
                if 'eng' in langs:
                    lang = 'eng'
                else:
                    lang = langs[0]
                raise DAError("could not get OCR language for language " + str(language) + "; using language " + str(lang) + "; error was " + str(the_error))
    return lang


def get_available_languages():
    if TESSERACT_MODE == LOCAL:
        try:
            output = subprocess.check_output([TESSERACT_PATH, '--list-langs'], stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as err:
            raise DAError("get_available_languages: failed to list available languages: " + str(err))
    elif TESSERACT_MODE == REMOTE:
        result = run_tesseract.delay(['--list-langs'], mode=1).get(disable_sync_subtasks=False)
        if not result.ok:
            raise DAError("get_available_languages: failed to list available languages")
        output = result.content
    else:
        raise DAError("get_available_languages: tesseract not installed")
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
    ocr_resolution = str(int(float(ocr_resolution)*11.0))
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
            except BaseException as the_error:
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
                raise DAError("document with extension " + doc.extension + " is not a readable image file")
            if doc.extension == 'pdf':
                # doc.page_path(1, 'page')
                with Pdf.open(doc.path()) as tmp_pdf:
                    page_count = len(tmp_pdf.pages)
                for i in range(page_count):
                    if f is not None and i + 1 < f:
                        continue
                    if l is not None and i + 1 > l:
                        continue
                    todo.append({'doc': doc, 'page': i+1, 'lang': lang, 'ocr_resolution': ocr_resolution, 'psm': psm, 'x': x, 'y': y, 'W': W, 'H': H, 'pdf_to_ppm': pdf_to_ppm, 'user_code': user_code, 'user': user, 'pdf': pdf, 'preserve_color': preserve_color})
            elif doc.extension in ("docx", "doc", "odt", "rtf"):
                doc_conv = pdf_concatenate(doc)
                with Pdf.open(doc_conv.path()) as tmp_pdf:
                    page_count = len(tmp_pdf.pages)
                for i in range(page_count):
                    if f is not None and i + 1 < f:
                        continue
                    if l is not None and i + 1 > l:
                        continue
                    todo.append({'doc': doc_conv, 'page': i+1, 'lang': lang, 'ocr_resolution': ocr_resolution, 'psm': psm, 'x': x, 'y': y, 'W': W, 'H': H, 'pdf_to_ppm': pdf_to_ppm, 'user_code': user_code, 'user': user, 'pdf': pdf, 'preserve_color': preserve_color})
            else:
                todo.append({'doc': doc, 'page': None, 'lang': lang, 'ocr_resolution': ocr_resolution, 'psm': psm, 'x': x, 'y': y, 'W': W, 'H': H, 'pdf_to_ppm': pdf_to_ppm, 'user_code': user_code, 'user': user, 'pdf': pdf, 'preserve_color': preserve_color})
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
    if prefix == 'page':
        flag = '-scale-to'
        resolution = int(float(resolution)*11.0)
    else:
        flag = '-r'
    if page is None:
        try:
            result = subprocess.run([str(pdf_to_ppm), flag, str(resolution), '-png', str(path), str(basefile + prefix)], timeout=3600, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        except subprocess.TimeoutExpired:
            result = 1
    else:
        try:
            result = subprocess.run([str(pdf_to_ppm), '-f', str(page), '-l', str(page), flag, str(resolution), '-png', str(path), str(basefile + prefix)], timeout=3600, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        except subprocess.TimeoutExpired:
            result = 1
    if os.path.isfile(test_path):
        os.remove(test_path)
    if result > 0:
        raise DAError("Unable to extract images from PDF file")


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
            if TESSERACT_MODE == LOCAL:
                try:
                    result = subprocess.run(params, timeout=60*60, check=False).returncode
                except subprocess.TimeoutExpired:
                    result = 1
                    logmessage("ocr_pdf: call to gs took too long")
            elif TESSERACT_MODE == REMOTE:
                result = run_gs.delay(params[1:]).get(disable_sync_subtasks=False)  # pylint: disable=possibly-used-before-assignment
                if result is None:
                    result = 1
                    logmessage("ocr_pdf: call to gs took too long")
            else:
                raise DAError("ocr_pdf: ghostscript not installed")
            if result != 0:
                raise DAError("ocr_pdf: failed to run gs with command " + " ".join(params))
            params = [TESSERACT_PATH, tiff_file.name, pdf_file.name, '-l', str(lang), '--psm', str(psm), '--dpi', '600', 'pdf']
            if TESSERACT_MODE == LOCAL:
                try:
                    result = subprocess.run(params, timeout=60*60, check=False).returncode
                except subprocess.TimeoutExpired:
                    result = 1
                    logmessage("ocr_pdf: call to tesseract took too long")
            elif TESSERACT_MODE == REMOTE:
                result = run_tesseract.delay(params[1:], mode=2).get(disable_sync_subtasks=False)
                if result.ok:
                    result = result.content
                else:
                    result = 1
                    logmessage("ocr_pdf: call to tesseract took too long")
            else:
                raise DAError("ocr_pdf: tesseract not installed")
            if result != 0:
                raise DAError("ocr_pdf: failed to run tesseract with command " + " ".join(params))
        else:
            params = [TESSERACT_PATH, path, pdf_file.name, '-l', str(lang), '--psm', str(psm), '--dpi', '300', 'pdf']
            if TESSERACT_MODE == LOCAL:
                try:
                    result = subprocess.run(params, timeout=60*60, check=False).returncode
                except subprocess.TimeoutExpired:
                    result = 1
                    logmessage("ocr_pdf: call to tesseract took too long")
            elif TESSERACT_MODE == REMOTE:
                result = run_tesseract.delay(params[1:], mode=2).get(disable_sync_subtasks=False)
                if result.ok:
                    result = result.content
                else:
                    result = 1
                    logmessage("ocr_pdf: call to tesseract took too long")
            else:
                raise DAError("ocr_pdf: tesseract not installed")
            if result != 0:
                raise DAError("ocr_pdf: failed to run tesseract with command " + " ".join(params))
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
    text = ''
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
        raise DAError("Not a readable image file")
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
                result = subprocess.run(args, timeout=120, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            except subprocess.TimeoutExpired:
                result = 1
            if result > 0:
                return word("(Unable to extract images from PDF file)")
            the_file = output_file.name + '.png'
    else:
        the_file = path
    file_to_read = tempfile.NamedTemporaryFile(prefix="datemp")
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
        file_to_read = tempfile.NamedTemporaryFile(prefix="datemp", suffix='.png')
        final_image.convert('RGBA').save(file_to_read, "PNG")
    file_to_read.seek(0)
    if pdf:
        outfile = doc._pdf_page_path(page)
        params = [TESSERACT_PATH, 'stdin', re.sub(r'\.pdf$', '', outfile), '-l', str(lang), '--psm', str(psm), '--dpi', str(ocr_resolution), 'pdf']
        logmessage("ocr_page: piping to command " + " ".join(params))
        if TESSERACT_MODE == LOCAL:
            try:
                text = subprocess.check_output(params, stdin=file_to_read).decode()
            except subprocess.CalledProcessError as err:
                raise DAError("ocr_page: failed to run tesseract with command " + " ".join(params) + ": " + str(err) + " " + str(err.output.decode()))
        elif TESSERACT_MODE == REMOTE:
            result = run_tesseract.delay(params[1:], mode=0, file_path=file_to_read.name).get(disable_sync_subtasks=False)
            if result.ok:
                text = result.content
            else:
                raise DAError("ocr_page: failed to run tesseract with command " + " ".join(params))
        else:
            raise DAError("ocr_page: tesseract not installed")
        logmessage("ocr_page finished with pdf page " + str(page))
        doc.commit()
        return {'indexno': indexno, 'page': page, 'doc': doc}
    params = [TESSERACT_PATH, 'stdin', 'stdout', '-l', str(lang), '--psm', str(psm), '--dpi', str(ocr_resolution)]
    logmessage("ocr_page: piping to command " + " ".join(params))
    if TESSERACT_MODE == LOCAL:
        try:
            text = subprocess.check_output(params, stdin=file_to_read).decode()
        except subprocess.CalledProcessError as err:
            raise DAError("ocr_page: failed to run tesseract with command " + " ".join(params) + ": " + str(err) + " " + str(err.output.decode()))
    elif TESSERACT_MODE == REMOTE:
        result = run_tesseract.delay(params[1:], mode=0, file_path=file_to_read.name).get(disable_sync_subtasks=False)
        if result.ok:
            text = result.content
        else:
            raise DAError("ocr_page: failed to run tesseract with command " + " ".join(params))
    logmessage("ocr_page finished with page " + str(page))
    return {'indexno': indexno, 'page': page, 'text': text}


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
    """Transform an object's docassemble variables into a JSON-serializable form.

    Args:
        obj (object): Python object (may contain DAObject instances, dates,
            etc.) to transform.

    Returns:
        object: A JSON-serializable version of ``obj``, with docassemble types
            converted to their plain Python equivalents.
    """
    return server.transform_json_variables(obj)
