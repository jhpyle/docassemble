import datetime
import copy
import httplib2
import apiclient
import time
import pytz
import yaml
import zipfile
import collections.abc as abc
from PIL import Image, ImageEnhance
from twilio.rest import Client as TwilioRestClient
import pycountry
import docassemble.base.ocr
import pickle
from itertools import chain
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError, DAValidationError, DAIndexError, DAWebError
from jinja2.runtime import UndefinedError
from jinja2.exceptions import TemplateError

import docassemble.base.pandoc
import docassemble.base.pdftk
import docassemble.base.file_docx
from docassemble.base.file_docx import include_docx_template
from docassemble.base.functions import alpha, roman, item_label, comma_and_list, get_language, set_language, get_dialect, set_country, get_country, word, comma_list, ordinal, ordinal_number, need, nice_number, quantity_noun, possessify, verb_past, verb_present, noun_plural, noun_singular, space_to_underscore, force_ask, force_gather, period_list, name_suffix, currency_symbol, currency, indefinite_article, nodoublequote, capitalize, title_case, url_of, do_you, did_you, does_a_b, did_a_b, were_you, was_a_b, have_you, has_a_b, your, her, his, their, is_word, get_locale, set_locale, process_action, url_action, get_info, set_info, get_config, prevent_going_back, qr_code, action_menu_item, from_b64_json, defined, define, value, message, response, json_response, command, single_paragraph, quote_paragraphs, location_returned, location_known, user_lat_lon, interview_url, interview_url_action, interview_url_as_qr, interview_url_action_as_qr, interview_email, get_emails, this_thread, static_image, action_arguments, action_argument, language_functions, language_function_constructor, get_default_timezone, user_logged_in, interface, user_privileges, user_has_privilege, user_info, background_action, background_response, background_response_action, background_error_action, us, set_live_help_status, chat_partners_available, phone_number_in_e164, phone_number_formatted, phone_number_is_valid, countries_list, country_name, write_record, read_records, delete_record, variables_as_json, all_variables, server, language_from_browser, device, plain, bold, italic, states_list, state_name, subdivision_type, indent, raw, fix_punctuation, set_progress, get_progress, referring_url, undefine, invalidate, dispatch, yesno, noyes, split, showif, showifdef, phone_number_part, set_parts, log, encode_name, decode_name, interview_list, interview_menu, server_capabilities, session_tags, get_chat_log, get_user_list, get_user_info, set_user_info, get_user_secret, create_user, create_session, get_session_variables, set_session_variables, get_question_data, go_back_in_session, manage_privileges, salutation, redact, ensure_definition, forget_result_of, re_run_logic, reconsider, set_title, set_save_status, single_to_double_newlines, CustomDataType, verbatim, add_separators, update_ordinal_numbers, update_ordinal_function, update_language_function, update_nice_numbers, update_word_collection, store_variables_snapshot, get_uid, update_terms
from docassemble.base.core import DAObject, DAList, DADict, DAOrderedDict, DASet, DAFile, DAFileCollection, DAStaticFile, DAFileList, DAEmail, DAEmailRecipient, DAEmailRecipientList, DATemplate, DAEmpty, DALink, selections, objects_from_file, RelationshipTree, DAContext, DACatchAll, DALazyTemplate
from decimal import Decimal
import sys
#sys.stderr.write("importing async mail now from util\n")
from docassemble.base.filter import markdown_to_html, to_text, ensure_valid_filename
from docassemble.base.generate_key import random_alphanumeric

#file_finder, url_finder, da_send_mail

import docassemble.base.filter
import dateutil
import dateutil.parser
import json
import codecs
import babel.dates
#import redis
import re
import phonenumbers
import tempfile
import os
import shutil
import subprocess
from bs4 import BeautifulSoup
import types
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from requests.exceptions import RequestException
import i18naddress
import docassemble.base.geocode

valid_variable_match = re.compile(r'^[^\d][A-Za-z0-9\_]*$')

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
    'explanation',
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
    'chain'
]

#knn_machine_learner = DummyObject

# def TheSimpleTextMachineLearner(*pargs, **kwargs):
#     return knn_machine_learner(*pargs, **kwargs)

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
    def set(self, key, value):
        """Writes an object to the data store under the given key."""
        the_key = self._get_base_key() + ':' + key
        server.server_sql_set(the_key, value, encrypted=self.is_encrypted(), secret=this_thread.current_info.get('secret', None), the_user_id=this_thread.current_info['user']['the_user_id'])
    def delete(self, key):
        """Deletes an object from the data store"""
        the_key = self._get_base_key() + ':' + key
        server.server_sql_delete(the_key)
    def keys(self):
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
        if not isinstance(task, (bool, str)):
            raise Exception("DAWeb.call: task_persistent must be boolean or string")
        return task_persistent
    def _get_auth(self, auth):
        if auth is None and hasattr(self, 'auth'):
            auth = self.auth
        if isinstance(auth, (dict, DADict)):
            if auth.get('type', 'basic') == 'basic':
                return HTTPBasicAuth(auth['username'], auth['password'])
            elif auth['type'] == 'digest':
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
            return True if json_body else False
        if hasattr(self, 'json_body'):
            return True if self.json_body else False
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
        elif isinstance(success_code, (abc.Iterable, DASet, DAList)):
            new_success_code = list()
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
            data = dict()
        if isinstance(data, DADict):
            data = data.elements
        if json_body is False and not isinstance(data, dict):
            raise Exception("DAWeb.call: data must be a dictionary")
        if params is None:
            params = dict()
        if isinstance(params, DADict):
            params = params.elements
        if not isinstance(params, dict):
            raise Exception("DAWeb.call: params must be a dictionary")
        if headers is None:
            headers = dict()
        if isinstance(headers, DADict):
            headers = headers.elements
        if not isinstance(headers, dict):
            raise Exception("DAWeb.call: the headers must be a dictionary")
        headers = self._get_headers(headers)
        if len(headers) == 0:
            headers = None
        if cookies is None:
            cookies = dict()
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
            new_files = dict()
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
                raise DAWebError(url=url, method=method, params=params, headers=headers, data=data, task=task, task_persistent=task_persistent, status_code=-1, response_text='', response_json=None, response_headers=dict(), exception_type=err.__class__.__name__, exception_text=str(err), cookies_before=cookies, cookies_after=None)
            else:
                return on_failure
        if success_code is None:
            if r.status_code >= 200 and r.status_code < 300:
                success = True
            else:
                success = False
        else:
            if r.status_code in success_code:
                success = True
            else:
                success = False
        if hasattr(self, 'cookies'):
            self.cookies = dict(r.cookies)
        try:
            json_response = r.json()
        except:
            json_response = None
        if success and task is not None:
            mark_task_as_performed(task, persistent=task_persistent)
        if not success:
            if on_failure == 'raise':
                raise DAWebError(url=url, method=method, params=params, headers=headers, data=data, task=task, task_persistent=task_persistent, status_code=r.status_code, response_text=r.text, response_json=json_response, response_headers=r.headers, exception_type=None, exception_text=None, cookies_before=cookies, cookies_after=dict(r.cookies), success=success)
            else:
                return on_failure
        if success and on_success is not None:
            if on_success == 'raise':
                raise DAWebError(url=url, method=method, params=params, headers=headers, data=data, task=task, task_persistent=task_persistent, status_code=r.status_code, response_text=r.text, response_json=json_response, response_headers=r.headers, exception_type=None, exception_text=None, cookies_before=cookies, cookies_after=dict(r.cookies), success=success)
            else:
                return on_success
        return(json_response if json_response is not None else r.text)
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
        return super().init(*pargs, **kwargs)
    @property
    def conn(self):
        """This property returns a boto3.resource('s3') or BlockBlobService() object."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).conn
        else:
            return server.cloud.conn
    @property
    def client(self):
        """This property returns a boto3.client('s3') object."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).client
        else:
            return server.cloud.client
    @property
    def bucket(self):
        """This property returns a boto3 Bucket() object."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).bucket
        else:
            return server.cloud.bucket
    @property
    def bucket_name(self):
        """This property returns the name of the Amazon S3 bucket."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).bucket_name
        else:
            return server.cloud.bucket_name
    @property
    def container_name(self):
        """This property returns the name of the Azure Blob Storage container."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).container
        else:
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
    def google_cloud_storage_client(self, scope=None):
        """Returns a google.cloud.storage.Client object."""
        return server.google_api.google_cloud_storage_client(scope)

def run_python_module(module, arguments=None):
    """Runs a python module, as though from the command line, and returns the output."""
    if re.search(r'\.py$', module):
        module = this_thread.current_package + '.' + re.sub(r'\.py$', '', module)
    elif re.search(r'^\.', module):
        module = this_thread.current_package + module
    commands = [re.sub(r'/lib/python.*', '/bin/python3', docassemble.base.ocr.__file__), '-m', module]
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

def today(timezone=None, format=None):
    """Returns today's date at midnight as a DADateTime object."""
    ensure_definition(timezone, format)
    if timezone is None:
        timezone = get_default_timezone()
    val = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(timezone))
    if format is not None:
        return dd(val.replace(hour=0, minute=0, second=0, microsecond=0)).format_date(format)
    else:
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
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        if as_word:
            return(babel.dates.format_date(date, format='MMMM', locale=babel_language(language)))
        return(int(date.strftime('%m')))
    except:
        return word("Bad date")

def day_of(the_date, language=None):
    """Interprets the_date as a date and returns the day of month."""
    ensure_definition(the_date, language)
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return(int(date.strftime('%d')))
    except:
        return word("Bad date")

def dow_of(the_date, as_word=False, language=None):
    """Interprets the_date as a date and returns the day of week as a number from 1 to 7 for Sunday through Saturday.  Set as_word to True if you want the day of week as a word."""
    ensure_definition(the_date, as_word, language)
    if language is None:
        language = get_language()
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        if as_word:
            return(babel.dates.format_date(date, format='EEEE', locale=babel_language(language)))
        else:
            return(int(date.strftime('%u')))
    except:
        return word("Bad date")

def year_of(the_date, language=None):
    """Interprets the_date as a date and returns the year."""
    ensure_definition(the_date, language)
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return(int(date.strftime('%Y')))
    except:
        return word("Bad date")

def interview_default(the_part, default_value, language):
    result = None
    if the_part in this_thread.internal and this_thread.internal[the_part] is not None:
         return this_thread.internal[the_part]
    for lang in (language, get_language(), '*'):
        if lang is not None:
            if lang in this_thread.interview.default_title:
                if the_part in this_thread.interview.default_title[lang]:
                    return this_thread.interview.default_title[lang][the_part]
    return default_value

def format_date(the_date, format=None, language=None):
    """Interprets the_date as a date and returns the date formatted for the current locale."""
    ensure_definition(the_date, format, language)
    if isinstance(the_date, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('date format', 'long', language)
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return babel.dates.format_date(date, format=format, locale=babel_language(language))
    except:
        return word("Bad date")

def format_datetime(the_date, format=None, language=None):
    """Interprets the_date as a date/time and returns the date/time formatted for the current locale."""
    ensure_definition(the_date, format, language)
    if isinstance(the_date, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('datetime format', 'long', language)
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return babel.dates.format_datetime(date, format=format, locale=babel_language(language))
    except:
        return word("Bad date")

def format_time(the_time, format=None, language=None):
    """Interprets the_time as a date/time and returns the time formatted for the current locale."""
    ensure_definition(the_time, format, language)
    if isinstance(the_time, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('time format', 'short', language)
    try:
        if isinstance(the_time, datetime.datetime) or isinstance(the_time, datetime.date) or isinstance(the_time, datetime.time):
            time = the_time
        else:
            time = dateutil.parser.parse(the_time)
        return babel.dates.format_time(time, format=format, locale=babel_language(language))
    except Exception as errmess:
        return word("Bad date: " + str(errmess))

class DateTimeDelta:
    def __str__(self):
        return str(self.describe())
    def describe(self, **kwargs):
        specificity = kwargs.get('specificity', None)
        output = list()
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
            else:
                return return_value
        else:
            return comma_and_list(["%d %s" % y for y in output])

class DADateTime(datetime.datetime):
    def format(self, format=None, language=None):
        return format_date(self, format=format, language=language)
    def format_date(self, format=None, language=None):
        return format_date(self, format=format, language=language)
    def format_datetime(self, format=None, language=None):
        return format_datetime(self, format=format, language=language)
    def format_time(self, format=None, language=None):
        return format_time(self, format=format, language=language)
    def replace_time(self, time):
        return self.replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=time.microsecond)
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
    return dd(pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(timezone)))

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
        new_datetime = new_datetime.astimezone(pytz.timezone(timezone))
    else:
        new_datetime = pytz.timezone(timezone).localize(new_datetime)
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
        starting = starting.astimezone(pytz.timezone(timezone))
    else:
        starting = pytz.timezone(timezone).localize(starting)
    if ending.tzinfo:
        ending = ending.astimezone(pytz.timezone(timezone))
    else:
        ending = pytz.timezone(timezone).localize(ending)
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
        if isinstance(person, Person) or isinstance(person, DAEmailRecipient):
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
    if isinstance(the_datetime, datetime.date) or isinstance(the_datetime, datetime.time):
        return True
    try:
        dateutil.parser.parse(the_datetime)
        return True
    except:
        return False

def timezone_list():
    """Returns a list of timezone choices, expressed as text."""
    return sorted([tz for tz in pytz.all_timezones])

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
        exclude_privileges = list()
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
        return dd(pytz.utc.localize(max_time).astimezone(pytz.timezone(timezone)))
    else:
        return dd(pytz.utc.localize(max_time).astimezone(pytz.utc))

def start_time(timezone=None):
    """Returns the time the interview was started, as a DADateTime object."""
    if timezone is not None:
        return dd(pytz.utc.localize(this_thread.internal['starttime']).astimezone(pytz.timezone(timezone)))
    else:
        return dd(pytz.utc.localize(this_thread.internal['starttime']).astimezone(pytz.utc))

class LatitudeLongitude(DAObject):
    """Represents a GPS location."""
    def init(self, *pargs, **kwargs):
        self.gathered = False
        self.known = False
        # self.description = ""
        return super().init(*pargs, **kwargs)
    def status(self):
        """Returns True or False depending on whether an attempt has yet been made
        to gather the latitude and longitude."""
        #logmessage("got to status")
        if self.gathered:
            #logmessage("gathered is true")
            return False
        else:
            if location_returned():
                #logmessage("returned is true")
                self._set_to_current()
                return False
            else:
                return True
    def _set_to_current(self):
        #logmessage("set to current")
        if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and isinstance(this_thread.current_info['user']['location'], dict):
            if 'latitude' in this_thread.current_info['user']['location'] and 'longitude' in this_thread.current_info['user']['location']:
                self.latitude = this_thread.current_info['user']['location']['latitude']
                self.longitude = this_thread.current_info['user']['location']['longitude']
                self.known = True
                #logmessage("known is true")
            elif 'error' in this_thread.current_info['user']['location']:
                self.error = this_thread.current_info['user']['location']['error']
                self.known = False
                #logmessage("known is false")
            self.gathered = True
            self.description = str(self)
        return
    def __str__(self):
        if hasattr(self, 'latitude') and hasattr(self, 'longitude'):
            return str(self.latitude) + ', ' + str(self.longitude)
        elif hasattr(self, 'error'):
            return str(self.error)
        return 'Unknown'

class RoleChangeTracker(DAObject):
    """Used within an interview to facilitate changes in the active role
    required for filling in interview information.  Ensures that participants
    do not receive multiple e-mails needlessly."""
    def init(self, *pargs, **kwargs):
        self.last_role = None
        return
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
        return
    def send_email(self, roles_needed, **kwargs):
        """Sends a notification e-mail if necessary because of a change in the
        active of the interviewee.  Returns True if an e-mail was
        successfully sent.  Otherwise, returns False.  False could
        mean that it was not necessary to send an e-mail."""
        #logmessage("Current role is " + str(this_thread.global_vars.role))
        for role_option in kwargs:
            if 'to' in kwargs[role_option]:
                need(kwargs[role_option]['to'].email)
        for role_needed in roles_needed:
            #logmessage("One role needed is " + str(role_needed))
            if role_needed == self.last_role:
                #logmessage("Already notified new role " + str(role_needed))
                return False
            if role_needed in kwargs:
                #logmessage("I have info on " + str(role_needed))
                email_info = kwargs[role_needed]
                if 'to' in email_info and 'email' in email_info:
                    #logmessage("I have email info on " + str(role_needed))
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
    def full(self):
        """Returns the full name."""
        return(self.text)
    def familiar(self):
        """Returns the familiar name."""
        return(self.text)
    def firstlast(self):
        """This method is included for compatibility with other types of names."""
        return(self.text)
    def lastfirst(self):
        """This method is included for compatibility with other types of names."""
        return(self.text)
    def middle_initial(self, with_period=True):
        """This method is included for compatibility with other types of names."""
        return('')
    def defined(self):
        """Returns True if the name has been defined.  Otherwise, returns False."""
        return hasattr(self, 'text')
    def __str__(self):
        return(str(self.full()))
#    def __repr__(self):
#        return(repr(self.full()))

class IndividualName(Name):
    """The name of an Individual."""
    def init(self, *pargs, **kwargs):
        if 'uses_parts' not in kwargs:
            self.uses_parts = True
        return super().init(*pargs, **kwargs)
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
    def full(self, middle='initial', use_suffix=True):
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
        return(" ".join(names))
    def firstlast(self):
        """Returns the first name followed by the last name."""
        if not self.uses_parts:
            return super().firstlast()
        return(self.first + " " + self.last)
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
        else:
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
        return super().init(*pargs, **kwargs)
    def __str__(self):
        return(str(self.block()))
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
        #if hasattr(self, 'sublocality') and self.sublocality:
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
    def get_geocode_response():
        """Returns the raw data that the geocoding service returned."""
        if hasattr(self, '_geocode_response') :
            return self._geocode_response
        elif hasattr(self, 'geolocate_response'):
            return self.geolocate_response
        if hasattr(self, 'norm'):
            if hasattr(self.norm, '_geocode_response'):
                return self.norm._geocode_response
            if hasattr(self.norm, 'geolocate_response'):
                return self.norm.geolocate_response
        return []
    def geolocate(self, address=None, reset=False):
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
                    return self._geocode_success
            elif self.geolocated:
                return self.geolocate_success
            the_address = self.on_one_line(omit_default_country=False)
        else:
            the_address = address
        #logmessage("geocode: trying to geocode " + str(the_address))
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
                assert success
            except Exception as the_err:
                logmessage(the_err.__class__.__name__ + ": " + str(the_err))
                try_number += 1
                time.sleep(try_number)
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
        #logmessage(str(self.__dict__))
        return self._geocode_success
    def normalize(self, long_format=False):
        if not self.geocode():
            return False
        the_instance_name = self.instanceName
        the_norm = self.norm
        the_norm_long = self.norm_long
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
        return(output)
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
                self.unit
            else:
                return ''
        if hasattr(self, 'unit') and self.unit != '' and self.unit is not None:
            if not re.search(r'unit|floor|suite|apt|apartment|room|ste|fl', str(self.unit), flags=re.IGNORECASE):
                return word("Unit", language=language) + " " + str(self.unit)
            else:
                return str(self.unit)
        elif hasattr(self, 'floor') and self.floor != '' and self.floor is not None:
            return word("Floor", language=language) + " " + str(self.floor)
        elif hasattr(self, 'room') and self.room != '' and self.room is not None:
            return word("Room", language=language) + " " + str(self.room)
        return ''
    def line_one(self, language=None):
        """Returns the first line of the address, including the unit
        number if there is one."""
        if self.city_only:
            return ''
        if (not hasattr(self, 'address')) and hasattr(self, 'street_number') and hasattr(self, 'street'):
            output += str(self.street_number) + " " + str(self.street)
        else:
            output = str(self.address)
        the_unit = self.formatted_unit(language=language)
        if the_unit != '':
            output += ", " + the_unit
        return(output)
    def line_two(self, language=None):
        """Returns the second line of the address, including the city,
        state and zip code."""
        output = ""
        #if hasattr(self, 'sublocality') and self.sublocality:
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
        return(output)

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
    elif part == 'alpha_3':
        return guess[0].alpha_3
    elif part == 'name':
        return guess[0].name
    elif part == 'numeric':
        return guess[0].numeric
    elif part == 'official_name':
        return guess[0].official_name
    else:
        raise DAError('iso_country: unknown part')

class City(Address):
    """A geographic address specific only to a city."""
    def init(self, *pargs, **kwargs):
        self.city_only = True
        return super().init(*pargs, **kwargs)

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
        return super().init(*pargs, **kwargs)
    def __setattr__(self, attrname, value):
        if attrname == 'name' and isinstance(value, str):
            self.name.text = value
        else:
            return super().__setattr__(attrname, value)
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
        return super().init(*pargs, **kwargs)
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
        return super().init(*pargs, **kwargs)
    def _map_info(self):
        if not self.location.known:
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
    def __setattr__(self, attrname, value):
        if attrname == 'name' and isinstance(value, str):
            self.name.text = value
        else:
            return super().__setattr__(attrname, value)
    def __str__(self):
        return str(self.name.full())
    def pronoun_objective(self, **kwargs):
        """Returns "it" or "It" depending on the value of the optional
        keyword argument "capitalize." """
        output = word('it', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def possessive(self, target, **kwargs):
        """Given a word like "fish," returns "your fish" or
        "John Smith's fish," depending on whether the person is the user."""
        if self is this_thread.global_vars.user:
            return your(target, **kwargs)
        else:
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
            return(capitalize(output))
        else:
            return(output)
    def is_user(self):
        """Returns True if the person is the user, otherwise False."""
        return self is this_thread.global_vars.user
    def address_block(self, language=None, international=False, show_country=False):
        """Returns the person name address as a block, for use in mailings."""
        if this_thread.evaluation_context == 'docx':
            return(self.name.full() + '</w:t><w:br/><w:t xml:space="preserve">' + self.address.block(language=language, international=international, show_country=show_country))
        else:
            return("[FLUSHLEFT] " + self.name.full() + " [NEWLINE] " + self.address.block(language=language, international=international, show_country=show_country))
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
            return('"' + nodoublequote(self.name) + '" <' + str(self.email) + '>')
        return(str(self.email))
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
            return(do_you(the_verb, **kwargs))
        else:
            return(does_a_b(self, the_verb, **kwargs))
    def did_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "did you eat" or "did John Smith eat,"
        depending on whether the person is the user."""
        if self == this_thread.global_vars.user:
            return did_you(the_verb, **kwargs)
        else:
            return did_a_b(self, the_verb, **kwargs)
    def were_question(self, the_target, **kwargs):
        """Given a target like "married", returns "were you married" or "was
        John Smith married," depending on whether the person is the
        user."""
        if self == this_thread.global_vars.user:
            return were_you(the_target, **kwargs)
        else:
            return was_a_b(self, the_target, **kwargs)
    def have_question(self, the_target, **kwargs):
        """Given a target like "", returns "have you married" or "has
        John Smith married," depending on whether the person is the
        user."""
        if self == this_thread.global_vars.user:
            return have_you(the_target, **kwargs)
        else:
            return has_a_b(self, the_target, **kwargs)
    def does_verb(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "eat" or "eats"
        depending on whether the person is the user."""
        if self == this_thread.global_vars.user:
            tense = '2sg'
        else:
            tense = '3sg'
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            return verb_past(the_verb, tense, **kwargs)
        else:
            return verb_present(the_verb, tense, **kwargs)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except uses the past tense of the verb."""
        if self == this_thread.global_vars.user:
            tense = "2sgp"
        else:
            tense = "3sgp"
        #logmessage(the_verb + " " + tense)
        output = verb_past(the_verb, tense, **kwargs)
    def subject(self, **kwargs):
        """Returns "you" or the person's name, depending on whether the
        person is the user."""
        if self == this_thread.global_vars.user:
            output = word('you', **kwargs)
        else:
            output = str(self)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)

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
        return super().init(*pargs, **kwargs)
    def familiar(self):
        """Returns the individual's familiar name."""
        return self.name.familiar()
    def get_parents(self, tree, create=False):
        return self.get_relation('child', tree, create=create)
    def get_spouse(self, tree, create=False):
        return self.get_peer_relation('spouse', tree, create=create)
    def set_spouse(self, target, tree):
        return self.set_peer_relationship(self, target, "spouse", tree, replace=True)
    def is_spouse_of(self, target, tree):
        return self.is_peer_relation(target, 'spouse', tree)
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
            else:
                return int(self.age)
        if as_of is None:
            comparator = current_datetime()
        else:
            comparator = as_datetime(as_of)
        birth_date = as_datetime(self.birthdate)
        rd = dateutil.relativedelta.relativedelta(comparator, birth_date)
        if decimals:
            return float(rd.years)
        else:
            return int(rd.years)
    def first_name_hint(self):
        """If the individual is the user and the user is logged in and
        the user has set up a name in the user profile, this returns
        the user's first name.  Otherwise, returns a blank string."""
        if self is this_thread.global_vars.user and this_thread.current_info['user']['is_authenticated'] and 'firstname' in this_thread.current_info['user'] and this_thread.current_info['user']['firstname']:
            return this_thread.current_info['user']['firstname'];
        return ''
    def last_name_hint(self):
        """If the individual is the user and the user is logged in and
        the user has set up a name in the user profile, this returns
        the user's last name.  Otherwise, returns a blank string."""
        if self is this_thread.global_vars.user and this_thread.current_info['user']['is_authenticated'] and 'lastname' in this_thread.current_info['user'] and this_thread.current_info['user']['lastname']:
            return this_thread.current_info['user']['lastname'];
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
            return(capitalize(output))
        else:
            return(output)
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
            return(capitalize(output))
        else:
            return(output)
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
            return(capitalize(output))
        else:
            return(output)
    def yourself_or_name(self, **kwargs):
        """Returns a "yourself" if the individual is the user, otherwise
        returns the individual's name."""
        if self == this_thread.global_vars.user:
            output = word('yourself', **kwargs)
        else:
            output = str(self)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def __setattr__(self, attrname, value):
        if attrname == 'name' and isinstance(value, str):
            if isinstance(self.name, IndividualName):
                self.name.uses_parts = False
            self.name.text = value
        else:
            return super().__setattr__(attrname, value)
    def __str__(self):
        if hasattr(self, 'use_familiar') and self.use_familiar and isinstance(self.name, IndividualName) and self.name.uses_parts:
            return str(self.name.first)
        return super().__str__()

class ChildList(DAList):
    """Represents a list of children."""
    ChildClass = Individual
    def init(self, *pargs, **kwargs):
        self.object_type = self.ChildClass
        return super().init(*pargs, **kwargs)

class Value(DAObject):
    """Represents a value in a FinancialList."""
    def amount(self):
        """Returns the value's amount, or 0 if the value does not exist."""
        if not self.exists:
            return 0
        return (Decimal(self.value))
    def __str__(self):
        return str(self.amount())
    def __float__(self):
        return float(self.amount())
    def __int__(self):
        return int(self.__float__())
    def __long__(self):
        return long(self.__float__())
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
        return super().init(*pargs, **kwargs)
    def total(self):
        """Returns the total value in the list, gathering the list items if necessary."""
        self._trigger_gather()
        result = 0
        for item in sorted(self.elements.keys()):
            if self[item].exists:
                result += Decimal(self[item].value)
        return(result)
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
        return super().init(*pargs, **kwargs)
    def total(self, period_to_use=1):
        """Returns the total periodic value in the list, gathering the list items if necessary."""
        self._trigger_gather()
        result = 0
        if period_to_use == 0:
            return(result)
        for item in sorted(self.elements.keys()):
            if self.elements[item].exists:
                result += Decimal(self.elements[item].value) * Decimal(self.elements[item].period)
        return(result/Decimal(period_to_use))
    def _new_item_init_callback(self):
        if hasattr(self, 'new_item_period'):
            self.elements[self.new_item_name].period = self.new_item_period
            del self.new_item_period
        return super()._new_item_init_callback()

class Income(PeriodicFinancialList):
    """A PeriodicFinancialList representing a person's income."""
    pass

class Asset(FinancialList):
    """A FinancialList representing a person's assets."""
    pass

class Expense(PeriodicFinancialList):
    """A PeriodicFinancialList representing a person's expenses."""
    pass

class OfficeList(DAList):
    """Represents a list of offices of a company or organization."""
    AddressClass = Address
    def init(self, *pargs, **kwargs):
        self.object_type = self.AddressClass
        return super().init(*pargs, **kwargs)

class Organization(Person):
    """Represents a company or organization."""
    OfficeListClass = OfficeList
    def init(self, *pargs, **kwargs):
        if 'offices' in kwargs:
            self.initializeAttribute('office', self.OfficeListClass)
            if type(kwargs['offices']) is list:
                for office in kwargs['offices']:
                    if type(office) is dict:
                        new_office = self.office.appendObject(**office)
                        new_office.geocode()
            del kwargs['offices']
        return super().init(*pargs, **kwargs)
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
        the_response = list()
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
        if len(the_response):
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
    message = server.sms_body(phone_number, body=body, config=config)
    #logmessage("Sending message " + str(message) + " to " + str(phone_number))
    send_sms(to=phone_number, body=message, config=config)

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
    if type(to) is not list:
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
    media = list()
    for attachment in attachments:
        attachment_list = list()
        if isinstance(attachment, DAFileCollection):
            subattachment = getattr(attachment, 'pdf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'docx', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'rtf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'tex', None)
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
                if type(the_attachment) is DAFile and the_attachment.ok:
                    #url = url_start + server.url_for('serve_stored_file', uid=this_thread.current_info['session'], number=the_attachment.number, filename=the_attachment.filename, extension=the_attachment.extension)
                    media.append(the_attachment.url_for(_external=True))
                if type(the_attachment) is DAStaticFile:
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
                    if len(media):
                        message = twilio_client.messages.create(to=phone_number, from_=from_number, body=body, media_url=media)
                    else:
                        message = twilio_client.messages.create(to=phone_number, from_=from_number, body=body)
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
        return info['FaxStatus']
    def pages(self):
        if self.sid is None:
            return 0
        the_json = server.server_redis.get('da:faxcallback:sid:' + self.sid)
        if the_json is None:
            return 0
        info = json.loads(the_json)
        return info.get('NumPages', 0)
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
        if the_status in ('received', 'delivered'):
            return True
        else:
            return False

def send_fax(fax_number, file_object, config='default', country=None):
    if server.twilio_config is None:
        logmessage("send_fax: ignoring because Twilio not enabled")
        return FaxStatus(None)
    if config not in server.twilio_config['name']:
        logmessage("send_fax: ignoring because requested configuration does not exist")
        return FaxStatus(None)
    tconfig = server.twilio_config['name'][config]
    if 'fax' not in tconfig or tconfig['fax'] in [False, None]:
        logmessage("send_fax: ignoring because fax not enabled")
        return FaxStatus(None)
    return FaxStatus(server.send_fax(fax_string(fax_number, country=country), file_object, config))

def send_email(to=None, sender=None, reply_to=None, cc=None, bcc=None, body=None, html=None, subject="", template=None, task=None, task_persistent=False, attachments=None, mailgun_variables=None, dry_run=False):
    """Sends an e-mail and returns whether sending the e-mail was successful."""
    if attachments is None:
        attachments = []
    if (not isinstance(attachments, (DAList, DASet, abc.Iterable))) or isinstance(attachments, str):
        attachments = [attachments]
    from flask_mail import Message
    if type(to) is not list:
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
    #logmessage("Sending mail to: " + repr(dict(subject=subject, recipients=to_string, sender=sender_string, cc=cc_string, bcc=bcc_string, body=body, html=html)))
    msg = Message(subject, sender=sender_string, reply_to=reply_to_string, recipients=to_string, cc=cc_string, bcc=bcc_string, body=body, html=html)
    if mailgun_variables is not None:
        if isinstance(mailgun_variables, dict):
            msg.mailgun_variables = mailgun_variables
        else:
            logmessage("send_email: mailgun_variables must be a dict")
    filenames_used = set()
    success = True
    for attachment in attachments:
        attachment_list = list()
        if isinstance(attachment, DAFileCollection):
            subattachment = getattr(attachment, 'pdf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'docx', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'rtf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'tex', None)
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
                        extension, mimetype = server.get_ext_and_mimetype(the_basename)
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
    return(success)

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
    the_map = {'markers': list()}
    all_args = list()
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
    if 'center' not in the_map and len(the_map['markers']):
        the_map['center'] = the_map['markers'][0]
    if len(the_map['markers']) or 'center' in the_map:
        return '[MAP ' + re.sub(r'\n', '', codecs.encode(json.dumps(the_map).encode('utf-8'), 'base64').decode()) + ']'
    return word('(Unable to display map)')

def ocr_file_in_background(*pargs, **kwargs):
    """Starts optical character recognition on one or more image files or PDF
    files and returns an object representing the background task created."""
    language = kwargs.get('language', None)
    psm = kwargs.get('psm', 6)
    x = kwargs.get('x', None)
    y = kwargs.get('y', None)
    W = kwargs.get('W', None)
    H = kwargs.get('H', None)
    message = kwargs.get('message', None)
    image_file = pargs[0]
    if len(pargs) > 1:
        ui_notification = pargs[1]
    else:
        ui_notification = None
    args = dict(yaml_filename=this_thread.current_info['yaml_filename'], user=this_thread.current_info['user'], user_code=this_thread.current_info['session'], secret=this_thread.current_info['secret'], url=this_thread.current_info['url'], url_root=this_thread.current_info['url_root'], language=language, psm=psm, x=x, y=y, W=W, H=H, extra=ui_notification, message=message, pdf=False, preserve_color=False)
    collector = server.ocr_finalize.s(**args)
    todo = list()
    indexno = 0
    for item in docassemble.base.ocr.ocr_page_tasks(image_file, **args):
        todo.append(server.ocr_page.s(indexno, **item))
        indexno += 1
    the_chord = server.chord(todo)(collector)
    if ui_notification is not None:
        worker_key = 'da:worker:uid:' + str(this_thread.current_info['session']) + ':i:' + str(this_thread.current_info['yaml_filename']) + ':userid:' + str(this_thread.current_info['user']['the_user_id'])
        #sys.stderr.write("worker_caller: id is " + str(result.obj.id) + " and key is " + worker_key + "\n")
        server.server_redis.rpush(worker_key, the_chord.id)
    #sys.stderr.write("ocr_file_in_background finished\n")
    return the_chord

# def ocr_file_in_background(image_file, ui_notification=None, language=None, psm=6, x=None, y=None, W=None, H=None):
#     """Starts optical character recognition on one or more image files or PDF
#     files and returns an object representing the background task created."""
#     sys.stderr.write("ocr_file_in_background: started\n")
#     return server.async_ocr(image_file, ui_notification=ui_notification, language=language, psm=psm, x=x, y=y, W=W, H=H, user_code=this_thread.current_info.get('session', None))

def ocr_file(image_file, language=None, psm=6, f=None, l=None, x=None, y=None, W=None, H=None):
    """Runs optical character recognition on one or more image files or PDF
    files and returns the recognized text."""
    if not (isinstance(image_file, DAFile) or isinstance(image_file, DAFileList)):
        return word("(Not a DAFile or DAFileList object)")
    pdf_to_ppm = get_config("pdftoppm")
    if pdf_to_ppm is None:
        pdf_to_ppm = 'pdftoppm'
    ocr_resolution = get_config("ocr dpi")
    if ocr_resolution is None:
        ocr_resolution = '300'
    lang = docassemble.base.ocr.get_ocr_language(language)
    if isinstance(image_file, DAFile):
        image_file = [image_file]
    temp_directory_list = list()
    file_list = list()
    for doc in image_file:
        if hasattr(doc, 'extension'):
            if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
                return word("(Not a readable image file)")
            path = doc.path()
            if doc.extension == 'pdf':
                directory = tempfile.mkdtemp()
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
                    result = subprocess.run(args, timeout=3600).returncode
                except subprocess.TimeoutExpired:
                    result = 1
                    logmessage("ocr_file: call to pdftoppm took too long")
                if result > 0:
                    return word("(Unable to extract images from PDF file)")
                file_list.extend(sorted([os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]))
                continue
            file_list.append(path)
    page_text = list()
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

def read_qr(image_file, f=None, l=None, x=None, y=None, W=None, H=None):
    """Reads QR codes from a file or files and returns a list of codes found."""
    if not (isinstance(image_file, DAFile) or isinstance(image_file, DAFileList)):
        return word("(Not a DAFile or DAFileList object)")
    if isinstance(image_file, DAFile):
        image_file = [image_file]
    pdf_to_ppm = get_config("pdftoppm")
    if pdf_to_ppm is None:
        pdf_to_ppm = 'pdftoppm'
    ocr_resolution = get_config("ocr dpi")
    if ocr_resolution is None:
        ocr_resolution = '300'
    file_list = list()
    temp_directory_list = list()
    for doc in image_file:
        if hasattr(doc, 'extension'):
            if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
                return word("(Not a readable image file)")
            path = doc.path()
            if doc.extension == 'pdf':
                directory = tempfile.mkdtemp()
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
                    result = subprocess.run(args, timeout=3600).returncode
                except subprocess.TimeoutExpired:
                    result = 1
                    logmessage("read_qr: call to pdftoppm took too long")
                if result > 0:
                    return word("(Unable to extract images from PDF file)")
                file_list.extend(sorted([os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]))
                continue
            file_list.append(path)
    codes = list()
    for page in file_list:
        from pyzbar.pyzbar import decode
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
        extension, mimetype = server.get_ext_and_mimetype(file_ref.filename)
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
        return super().init(*pargs, **kwargs)
    def __str__(self):
        return str(self.prediction)
    def predict(self):
        if self.use_for_training:
            self.entry_id = self.learner.save_for_classification(self.text, key=self.key)
        self.predictions = self.learner.predict(self.text, probabilities=True)
        if len(self.predictions):
            self.prediction = self.predictions[0][0]
            self.probability = self.predictions[0][1]
        else:
            self.prediction = None
            self.probability = 1.0

def docx_concatenate(*pargs, **kwargs):
    """Concatenates DOCX files together and returns a DAFile representing
    the new DOCX file.

    """
    paths = list()
    get_docx_paths([x for x in pargs], paths)
    if len(paths) == 0:
        raise DAError("docx_concatenate: no valid files to concatenate")
    docx_path = docassemble.base.file_docx.concatenate_files(paths)
    docx_file = DAFile()._set_instance_name_for_function()
    docx_file.initialize(filename=kwargs.get('filename', 'file.docx'))
    docx_file.copy_into(docx_path)
    docx_file.retrieve()
    docx_file.commit()
    return docx_file

def get_docx_paths(target, paths):
    if isinstance(target, DAFileCollection) and hasattr(target, 'docx'):
        paths.append(target.docx.path())
    elif isinstance(target, DAFileList) or isinstance(target, DAList) or (isinstance(target, abc.Iterable) and not isinstance(target, str)):
        for the_file in target:
            get_docx_paths(the_file, paths)
    elif isinstance(target, DAFile) or isinstance(target, DAStaticFile):
        paths.append(target.path())
    elif isinstance(target, str) and os.path.isfile(target):
        paths.append(target)

def pdf_concatenate(*pargs, **kwargs):
    """Concatenates PDF files together and returns a DAFile representing
    the new PDF.

    """
    paths = list()
    get_pdf_paths([x for x in pargs], paths)
    if len(paths) == 0:
        raise DAError("pdf_concatenate: no valid files to concatenate")
    pdf_path = docassemble.base.pandoc.concatenate_files(paths, pdfa=kwargs.get('pdfa', False), password=kwargs.get('password', None))
    pdf_file = DAFile()._set_instance_name_for_function()
    pdf_file.initialize(filename=kwargs.get('filename', 'file.pdf'))
    pdf_file.copy_into(pdf_path)
    pdf_file.retrieve()
    pdf_file.commit()
    return pdf_file

def get_pdf_paths(target, paths):
    if isinstance(target, DAFileCollection) and hasattr(target, 'pdf'):
        paths.append(target.pdf.path())
    elif isinstance(target, DAFileList) or isinstance(target, DAList) or (isinstance(target, abc.Iterable) and not isinstance(target, str)):
        for the_file in target:
            get_pdf_paths(the_file, paths)
    elif isinstance(target, DAFile) or isinstance(target, DAStaticFile):
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
    elif isinstance(param, DAStaticFile) or isinstance(param, DAFile):
        files.append((root + param.filename, param.path()))
    else:
        file_info = server.file_finder(param)
        files.append((root + file_info['filename'], file_info['fullpath']))
    return files

def zip_file(*pargs, **kwargs):
    """Returns a ZIP file as a DAFile containing the files provided as arguments."""
    files = list()
    timezone = get_default_timezone()
    recurse_zip_params(pargs, '', files)
    zip_file = DAFile()._set_instance_name_for_function()
    zip_file.initialize(filename=kwargs.get('filename', 'file.zip'))
    zf = zipfile.ZipFile(zip_file.path(), mode='w')
    seen = dict()
    for zip_path, path in files:
        if zip_path not in seen:
            seen[zip_path] = 0
        seen[zip_path] += 1
    revised_files = list()
    count = dict()
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
        info.date_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(path)).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone)).timetuple()
        with open(path, 'rb') as fp:
            zf.writestr(info, fp.read())
    zf.close()
    zip_file.retrieve()
    zip_file.commit()
    return zip_file

def validation_error(message, field=None):
    """Raises a validation error with a given message, optionally
    associated with a field.

    """
    raise DAValidationError(message, field=field)

def invalid_variable_name(varname):
    if not isinstance(varname, str):
        return True
    if re.search(r'[\n\r\(\)\{\}\*\^\#]', varname):
        return True
    varname = re.sub(r'[\.\[].*', '', varname)
    if not valid_variable_match.match(varname):
        return True
    return False

contains_volatile = re.compile('^(x\.|x\[|.*\[[ijklmn]\])')

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
                    variables.append(dict(action=var, arguments=dict()))
            for command in ('undefine', 'invalidate', 'recompute'):
                if command not in the_saveas:
                    continue
                if not isinstance(the_saveas[command], list):
                    raise DAError("url_ask: the " + command + " statement must refer to a list.  " + repr(data))
                clean_list = []
                for undef_var in the_saveas[command]:
                    if not isinstance(undef_var, str):
                        raise DAError("url_ask: invalid variable name " + repr(undef_var) + " in " + command + ".  " + repr(data))
                    undef_saveas = undef_var.strip()
                    if invalid_variable_name(undef_saveas):
                        raise DAError("url_ask: missing or invalid variable name " + repr(undef_saveas) + " .  " + repr(data))
                    if contains_volatile.search(undef_saveas):
                        raise DAError("url_ask cannot be used with a generic object or a variable iterator")
                    clean_list.append(undef_saveas)
                if command == 'invalidate':
                    variables.append(dict(action='_da_invalidate', arguments=dict(variables=clean_list)))
                else:
                    variables.append(dict(action='_da_undefine', arguments=dict(variables=clean_list)))
                if command == 'recompute':
                    variables.append(dict(action='_da_compute', arguments=dict(variables=clean_list)))
            continue
        if isinstance(the_saveas, dict) and len(the_saveas) == 2 and 'action' in the_saveas and 'arguments' in the_saveas:
            if not isinstance(the_saveas['arguments'], dict):
                raise DAError("url_ask: an arguments directive must refer to a dictionary.  " + repr(data))
            if contains_volatile.search(the_saveas['action']):
                raise DAError("url_ask cannot be used with a generic object or a variable iterator")
            variables.append(dict(action=the_saveas['action'], arguments=the_saveas['arguments']))
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
        target = 'target="_blank"'
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

def overlay_pdf(main_pdf, logo_pdf, first_page=None, last_page=None, logo_page=None, only=None):
    """Overlays a page from a PDF file on top of the pages of another PDF file."""
    if isinstance(main_pdf, DAFileCollection):
        main_file = main_pdf.pdf.path()
    elif isinstance(main_pdf, DAFile) or isinstance(main_pdf, DAStaticFile) or isinstance(main_pdf, DAFileList):
        main_file = main_pdf.path()
    elif isinstance(main_pdf, str):
        main_file = main_pdf
    else:
        raise Exception("overlay_pdf: bad main filename")
    if isinstance(logo_pdf, DAFileCollection):
        logo_file = logo_pdf.pdf.path()
    elif isinstance(logo_pdf, DAFile) or isinstance(logo_pdf, DAStaticFile) or isinstance(logo_pdf, DAFileList):
        logo_file = logo_pdf.path()
    elif isinstance(logo_pdf, str):
        logo_file = logo_pdf
    else:
        raise Exception("overlay_pdf: bad logo filename")
    outfile = DAFile()
    outfile.set_random_instance_name()
    outfile.initialize(extension='pdf')
    docassemble.base.pdftk.overlay_pdf(main_file, logo_file, outfile.path(), first_page=first_page, last_page=last_page, logo_page=logo_page, only=only)
    outfile.commit()
    outfile.retrieve()
    return outfile

def explain(explanation, category='default'):
    """Add a line to the explanations history."""
    if 'explanations' not in this_thread.internal:
        this_thread.internal['explanations'] = dict()
    if category not in this_thread.internal['explanations']:
        this_thread.internal['explanations'][category] = list()
    if explanation not in this_thread.internal['explanations'][category]:
        this_thread.internal['explanations'][category].append(explanation)

def clear_explanations(category='default'):
    """Erases the history of explanations."""
    if 'explanations' not in this_thread.internal:
        return
    if category == 'all':
        this_thread.internal['explanations'] = dict()
    if category not in this_thread.internal['explanations']:
        return
    this_thread.internal['explanations'][category] = list()

def explanation(category='default'):
    """Returns the list of explanations."""
    if 'explanations' not in this_thread.internal:
        return []
    return this_thread.internal['explanations'].get(category, [])

def set_status(**kwargs):
    """Sets various settings in the interview session."""
    if 'misc' not in this_thread.internal:
        this_thread.internal['misc'] = dict()
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
        except (NameError, AttributeError, DAIndexError, UndefinedError) as err:
            raise Exception("Reference to undefined variable in context where dependency satisfaction not allowed")
        # Python 3 version:
        # try:
        #     return f(*args, **kwargs)
        # except (NameError, AttributeError, DAIndexError, UndefinedError) as err:
        #     raise Exception("Reference to undefined variable in context where dependency satisfaction not allowed") from err
    return wrapper

def assemble_docx(input_file, fields=None, output_path=None, output_format='docx', return_content=False, pdf_options=None, filename=None):
    import docassemble.base.parse
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
        docx_template = docassemble.base.file_docx.DocxTemplate(input_file)
        docassemble.base.functions.set_context('docx', template=docx_template)
        the_env = docassemble.base.parse.custom_jinja_env()
        the_xml = docx_template.get_xml()
        the_xml = re.sub(r'<w:p>', '\n<w:p>', the_xml)
        the_xml = re.sub(r'({[\%\{].*?[\%\}]})', docassemble.base.parse.fix_quotes, the_xml)
        the_xml = docx_template.patch_xml(the_xml)
        parsed_content = the_env.parse(the_xml)
        while True:
            old_count = docassemble.base.functions.this_thread.misc.get('docx_include_count', 0)
            docx_template.render(the_fields, jinja_env=docassemble.base.parse.custom_jinja_env())
            if docassemble.base.functions.this_thread.misc.get('docx_include_count', 0) > old_count and old_count < 10:
                new_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
                docx_template.save(new_template_file.name)
                docx_template = docassemble.base.file_docx.DocxTemplate(new_template_file.name)
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
            pdf_options = dict()
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
    import docassemble.base.parse
    return docassemble.base.parse.register_jinja_filter(filter_name, func)

from docassemble.base.oauth import DAOAuth

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
        store.set('tasks', dict())
    return store

def task_performed(task, persistent=False):
    """Returns True if the task has been performed at least once, otherwise False."""
    ensure_definition(task)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        if task in tasks and tasks[task]:
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
        if not task in tasks:
            tasks[task] = 0
        tasks[task] += 1
        store.set('tasks', tasks)
        return tasks[task]
    if not task in this_thread.internal['tasks']:
        this_thread.internal['tasks'][task] = 0
    this_thread.internal['tasks'][task] += 1
    return this_thread.internal['tasks'][task]

def times_task_performed(task, persistent=False):
    """Returns the number of times the task has been performed."""
    ensure_definition(task)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        if not task in tasks:
            return 0
        return tasks[task]
    if not task in this_thread.internal['tasks']:
        return 0
    return this_thread.internal['tasks'][task]

def set_task_counter(task, times, persistent=False):
    """Allows you to manually set the number of times the task has been performed."""
    ensure_definition(task, times)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        tasks[task] = times
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
