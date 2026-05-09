import re
import types
import os
import locale
import decimal
from io import IOBase
import codecs
import copy
import base64
import json
import ast
import datetime
import threading
import random
from collections.abc import Iterable
from unicodedata import normalize
from enum import Enum
from pathlib import Path
import importlib.resources
import sys
import astunparse
import tzlocal
import us
import pycountry
import markdown
import ruamel.yaml
from types import SimpleNamespace
from docassemble.base.save_status import SS_NEW, SS_OVERWRITE, SS_IGNORE
from docassemble.base.pattern import pattern_en, pattern_es, pattern_de, pattern_fr, pattern_it, pattern_nl

from pylatex.utils import escape_latex
# import operator
import titlecase
from user_agents import parse as ua_parse
import phonenumbers
import werkzeug.utils
import num2words
from jinja2.runtime import Undefined
from docassemble.base.logger import logmessage  # pylint: disable=ungrouped-imports
from docassemble.base.error import ForcedNameError, QuestionError, ResponseError, CommandError, BackgroundResponseError, BackgroundResponseActionError, ForcedReRun, DAError, DANameError, DAInvalidFilename
from docassemble.base.generate_key import random_string
import docassemble.base.astparser
FileType = IOBase
equals_byte = bytes('=', 'utf-8')
TypeType = type(type(None))
locale.setlocale(locale.LC_ALL, '')
contains_volatile = re.compile(r'^(x\.|x\[|.*\[[ijklmn]\])')
match_brackets_or_dot = re.compile(r'(\[.+?\]|\.[a-zA-Z_][a-zA-Z0-9_]*)')
python313 = sys.version_info >= (3, 13)

__all__ = ['alpha', 'roman', 'item_label', 'ordinal', 'ordinal_number', 'comma_list', 'word', 'get_language', 'set_language', 'get_dialect', 'set_country', 'get_country', 'get_locale', 'set_locale', 'comma_and_list', 'need', 'nice_number', 'quantity_noun', 'currency_symbol', 'verb_past', 'verb_present', 'noun_plural', 'noun_singular', 'indefinite_article', 'capitalize', 'space_to_underscore', 'force_ask', 'period_list', 'name_suffix', 'currency', 'static_image', 'title_case', 'url_of', 'process_action', 'url_action', 'get_info', 'set_info', 'get_config', 'prevent_going_back', 'qr_code', 'action_menu_item', 'from_b64_json', 'defined', 'value', 'message', 'response', 'json_response', 'command', 'background_response', 'background_response_action', 'single_paragraph', 'quote_paragraphs', 'location_returned', 'location_known', 'user_lat_lon', 'interview_url', 'interview_url_action', 'interview_url_as_qr', 'interview_url_action_as_qr', 'interview_email', 'get_emails', 'action_arguments', 'action_argument', 'get_default_timezone', 'user_logged_in', 'user_privileges', 'user_has_privilege', 'user_info', 'current_context', 'background_action', 'background_response', 'background_response_action', 'us', 'set_live_help_status', 'chat_partners_available', 'phone_number_in_e164', 'phone_number_formatted', 'phone_number_is_valid', 'countries_list', 'country_name', 'write_record', 'read_records', 'delete_record', 'variables_as_json', 'all_variables', 'language_from_browser', 'device', 'plain', 'bold', 'italic', 'subdivision_type', 'indent', 'raw', 'fix_punctuation', 'set_progress', 'get_progress', 'referring_url', 'undefine', 'invalidate', 'dispatch', 'yesno', 'noyes', 'phone_number_part', 'log', 'encode_name', 'decode_name', 'interview_list', 'interview_menu', 'server_capabilities', 'session_tags', 'get_chat_log', 'get_user_list', 'get_user_info', 'set_user_info', 'get_user_secret', 'create_user', 'invite_user', 'create_session', 'get_session_variables', 'set_session_variables', 'go_back_in_session', 'manage_privileges', 'redact', 'forget_result_of', 're_run_logic', 'reconsider', 'get_question_data', 'set_save_status', 'single_to_double_newlines', 'verbatim', 'add_separators', 'store_variables_snapshot', 'update_terms', 'set_variables', 'language_name', 'run_action_in_session']

# debug = False
# default_dialect = 'us'
# default_language = 'en'
# default_locale = 'US.utf8'
# default_country = 'US'

# try:
#     default_timezone = tzlocal.get_localzone().zone
# except:
#     default_timezone = 'America/New_York'
# daconfig = {}
dot_split = re.compile(r'([^\.\[\]]+(?:\[.*?\])?)')
newlines = re.compile(r'[\r\n]+')
single_newline = re.compile(r'[\r\n]')


class RawValue:

    def __init__(self, the_value):
        self.value = the_value


def raw(val):
    """Pass a value as-is to a DOCX template without converting it to text.

    Wraps the value so that Jinja2 template code can use it directly,
    for example as a list or other Python object rather than a string.

    Args:
        val: The value to pass through without text conversion.

    Returns:
        RawValue: A wrapper object containing the original value.
    """
    return RawValue(val)


class ReturnValue:  # This class is defined here for backwards-compatibility reasons because it might be pickled in existing data.

    def __init__(self, **kwargs):
        self.extra = kwargs.get('extra', None)
        self.value = kwargs.get('value', None)
        for key, val in kwargs.items():
            if key not in ['extra', 'value']:
                setattr(self, key, val)

    def __str__(self):
        if hasattr(self, 'ok') and self.ok and hasattr(self, 'content'):
            return str(self.content)
        if hasattr(self, 'error_message'):
            return str(self.error_message)
        return str(self.value)


def filename_invalid(filename):
    if '../' in filename or filename.startswith('/'):
        return True
    if re.search(r'[^A-Za-z0-9\_\.\-\/ ]', filename):
        return True
    if len(filename) > 268:
        return True
    return False


def package_name_invalid(packagename):
    if re.search(r'[^A-Za-z0-9\_\.\-]', packagename):
        return True
    if len(packagename) > 268:
        return True
    if not packagename.startswith('docassemble.'):
        return True
    return False


def get_current_variable():
    # logmessage("get_current_variable")
    if len(this_thread.current_variable) > 0:
        return this_thread.current_variable[-1]
    # logmessage("get_current_variable: no current variable")
    return None


def reset_context():
    this_thread.evaluation_context = None
    if 'docx_include_count' in this_thread.misc:
        del this_thread.misc['docx_include_count']
    if 'docx_template' in this_thread.misc:
        del this_thread.misc['docx_template']


def set_context(new_context, template=None):
    this_thread.evaluation_context = new_context
    this_thread.misc['docx_include_count'] = 0
    this_thread.misc['docx_template'] = template


def set_current_variable(var):
    # logmessage("set_current_variable: " + str(var))
    # if len(this_thread.current_variable) > 0 and this_thread.current_variable[-1] == var:
    #     return
    this_thread.current_variable.append(var)


def pop_event_stack(var):
    unique_id = this_thread.current_info['user']['session_uid']
    if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack']:
        if len(this_thread.internal['event_stack'][unique_id]) > 0 and this_thread.internal['event_stack'][unique_id][0]['action'] == var:
            this_thread.internal['event_stack'][unique_id].pop(0)
            # logmessage("popped the event stack")
    if 'action' in this_thread.current_info and this_thread.current_info['action'] == var:
        del this_thread.current_info['action']


def pop_current_variable():
    # logmessage("pop_current_variable: " + str(this_thread.current_variable))
    if len(this_thread.current_variable) > 0:
        var = this_thread.current_variable.pop()
        # logmessage("pop_current_variable: " + str(var))
        return var
    # logmessage("pop_current_variable: None")
    return None


def wrap_up():
    while len(this_thread.open_files) > 0:
        file_object = this_thread.open_files.pop()
        file_object.commit()


def set_gathering_mode(mode, instanceName):
    # logmessage("set_gathering_mode: " + str(instanceName) + " with mode " + str(mode))
    if mode:
        if instanceName not in this_thread.gathering_mode:
            # logmessage("set_gathering_mode: using " + str(get_current_variable()))
            this_thread.gathering_mode[instanceName] = get_current_variable()
    else:
        try:
            del this_thread.gathering_mode[instanceName]
        except KeyError:
            pass


def get_gathering_mode(instanceName):
    # logmessage("get_gathering_mode: " + str(instanceName))
    if instanceName not in this_thread.gathering_mode:
        # logmessage("get_gathering_mode: returning False")
        return False
    # logmessage("get_gathering_mode: returning True")
    return True


def reset_gathering_mode(*pargs):
    # logmessage("reset_gathering_mode: " + repr([y for y in pargs]))
    if len(pargs) == 0:
        this_thread.gathering_mode = {}
        return
    var = pargs[0]
    todel = []
    for instanceName, curVar in this_thread.gathering_mode.items():
        if curVar == var:
            todel.append(instanceName)
    # logmessage("reset_gathering_mode: deleting " + repr([y for y in todel]))
    for item in todel:
        try:
            del this_thread.gathering_mode[item]
        except KeyError:
            pass


def set_uid(uid):
    this_thread.session_id = uid


def get_uid():
    try:
        if this_thread.session_id is not None:
            return this_thread.session_id
    except:
        pass
    try:
        return this_thread.current_info['session']
    except:
        return None


def get_chat_log(utc=False, timezone=None):
    """Return the messages in the chat log of the current interview session.

    Args:
        utc (bool, optional): If True, return times in UTC. Defaults to False.
        timezone (str, optional): Timezone name to use for timestamps (e.g.,
            ``'America/New_York'``). Defaults to None.

    Returns:
        list: A list of chat messages for the current interview session.
    """
    return server.get_chat_log(this_thread.current_info.get('yaml_filename', None), this_thread.current_info.get('session', None), this_thread.current_info.get('secret', None), utc=utc, timezone=timezone)


def get_current_package():
    if this_thread.current_package is not None:
        return this_thread.current_package
    return None


def get_current_question():
    if this_thread.current_question is not None:
        return this_thread.current_question
    return None


def user_logged_in():
    """Return True if the user is logged in, False otherwise.

    Returns:
        bool: True if the current user is authenticated, False otherwise.
    """
    if this_thread.current_info['user']['is_authenticated']:
        return True
    return False


def device(ip=False):
    """Return information about the user's device or IP address.

    Args:
        ip (bool, optional): If True, return the user's IP address as a string
            instead of device information. Defaults to False.

    Returns:
        object: A user-agent object with browser and device information, or
            a string IP address when ``ip=True``. Returns None if device
            information cannot be determined.
    """
    if ip:
        return this_thread.current_info['clientip']
    if 'headers' in this_thread.current_info:
        ua_string = this_thread.current_info['headers'].get('User-Agent', None)
        if ua_string is not None:
            the_response = ua_parse(ua_string)
        else:
            the_response = None
    else:
        the_response = None
    return the_response


def parse_accept_language(language_header, restrict=True):
    ok_languages = set()
    for lang in word_collection:
        ok_languages.add(lang)
    languages = []
    for item in language_header.split(','):
        q = 1.0
        lang = item.strip()
        if ';' in lang:
            parts = item.split(';')
            lang = parts[0]
            q = parts[1]
            try:
                q = float(re.sub(r'^q=', '', q, flags=re.IGNORECASE))
            except:
                q = 1.0

        parts = re.split('-|_', lang)

        languages.append([parts[0].strip().lower(), q])
    output = []
    for item in sorted(languages, key=lambda y: y[1], reverse=True):
        if restrict and item[0] not in ok_languages:
            continue
        if item[0] not in output:
            output.append(item[0])
    return output


def language_from_browser(*pargs):
    """Return the user's preferred language based on the browser's Accept-Language header.

    Reads the Accept-Language HTTP header and returns the first recognized
    ISO-639-1, ISO-639-2, or ISO-639-3 language code. If called with arguments,
    only languages in the argument list are considered valid.

    Args:
        *pargs: Optional list of valid language codes. If provided, only these
            codes are considered, and None is returned if the browser's preferred
            language is not in the list.

    Returns:
        str: A language code (e.g., ``'en'``, ``'es'``) or None if the language
            cannot be determined.
    """
    if len(pargs) > 0:
        restrict = True
        valid_options = list(pargs)
    else:
        restrict = False
        valid_options = []
    if 'headers' in this_thread.current_info:
        language_header = this_thread.current_info['headers'].get('Accept-Language', None)
        if language_header is not None:
            langs = parse_accept_language(language_header, restrict=False)
        else:
            return None
    else:
        return None
    for lang in langs:
        if restrict:
            if lang in valid_options:
                return lang
            continue
        if len(lang) == 2:
            try:
                pycountry.languages.get(alpha_2=lang)
                return lang
            except:
                continue
        if len(lang) == 3:
            try:
                pycountry.languages.get(alpha_3=lang)
                return lang
            except:
                continue
    for lang in langs:
        if len(lang) <= 3:
            continue
        this_lang = re.sub(r'[\-\_].*', r'', lang)
        if restrict:
            if this_lang in valid_options:
                return this_lang
            continue
        if len(this_lang) == 2:
            try:
                pycountry.languages.get(alpha_2=this_lang)
                return this_lang
            except:
                continue
        if len(this_lang) == 3:
            try:
                pycountry.languages.get(alpha_3=this_lang)
                return this_lang
            except:
                continue
    return None


def country_name(country_code):
    """Return the full name of a country given its two-letter ISO 3166-1 alpha-2 code.

    The name is passed through the ``word()`` function for translation.

    Args:
        country_code (str): A two-letter, capitalized country code (e.g., ``'US'``, ``'DE'``).

    Returns:
        str: The full name of the country in the current language.
    """
    ensure_definition(country_code)
    return word(pycountry.countries.get(alpha_2=country_code).name)


def state_name(state_code, country_code=None):
    """Return the full name of a U.S. state or country subdivision given its abbreviation.

    Args:
        state_code (str): The abbreviated code for the state or subdivision
            (e.g., ``'NY'`` for New York).
        country_code (str, optional): A two-letter ISO 3166-1 alpha-2 country
            code. Defaults to the current country as returned by ``get_country()``.

    Returns:
        str: The full name of the state or subdivision, passed through ``word()``
            for translation. Returns the original ``state_code`` if not found.
    """
    ensure_definition(state_code, country_code)
    if country_code is None:
        country_code = get_country() or 'US'
    for subdivision in pycountry.subdivisions.get(country_code=country_code):
        m = re.search(r'-([A-Z0-9]+)$', subdivision.code)
        if m and m.group(1) == state_code:
            return word(subdivision.name)
    return state_code
    # return us.states.lookup(state_code).name


def language_name(language_code):
    """Return the full name of a language given its ISO-639-1 or ISO-639-3 code.

    The language name is passed through the ``word()`` function for translation.
    If the language cannot be found, the original code is returned (also via
    ``word()``).

    Args:
        language_code (str): A two-letter ISO-639-1 code (e.g., ``'en'``) or
            three-letter ISO-639-3 code (e.g., ``'eng'``).

    Returns:
        str: The full name of the language (e.g., ``'English'``).
    """
    ensure_definition(language_code)
    try:
        if len(language_code) == 2:
            return word(pycountry.languages.get(alpha_2=language_code).name)
        return word(pycountry.languages.get(alpha_3=language_code).name)
    except:
        return word(language_code)


def subdivision_type(country_code):
    """Return the name of the primary subdivision type for the given country.

    For example, returns ``'State'`` for ``'US'``, ``'Province'`` for ``'CA'``.
    Returns None if the country has no subdivisions.

    Args:
        country_code (str): A two-letter ISO 3166-1 alpha-2 country code.

    Returns:
        str: The name of the most common first-level subdivision type, or None
            if the country has no subdivisions.
    """
    ensure_definition(country_code)
    counts = {}
    for subdivision in pycountry.subdivisions.get(country_code=country_code):
        if subdivision.parent_code is not None:
            continue
        if subdivision.type not in counts:
            counts[subdivision.type] = 1
        else:
            counts[subdivision.type] += 1
    counts_ordered = sorted(counts.keys(), key=lambda x: counts[x], reverse=True)
    if len(counts_ordered) > 1 and counts[counts_ordered[1]] > 0.5*counts[counts_ordered[0]]:
        return word(counts_ordered[0] + '/' + counts_ordered[1])
    if len(counts_ordered) > 0:
        return word(counts_ordered[0])
    return None

# word('Aruba')
# word('Afghanistan')
# word('Angola')
# word('Anguilla')
# word('Åland Islands')
# word('Albania')
# word('Andorra')
# word('United Arab Emirates')
# word('Argentina')
# word('Armenia')
# word('American Samoa')
# word('Antarctica')
# word('French Southern Territories')
# word('Antigua and Barbuda')
# word('Australia')
# word('Austria')
# word('Azerbaijan')
# word('Burundi')
# word('Belgium')
# word('Benin')
# word('Bonaire, Sint Eustatius and Saba')
# word('Burkina Faso')
# word('Bangladesh')
# word('Bulgaria')
# word('Bahrain')
# word('Bahamas')
# word('Bosnia and Herzegovina')
# word('Saint Barthélemy')
# word('Belarus')
# word('Belize')
# word('Bermuda')
# word('Bolivia, Plurinational State of')
# word('Brazil')
# word('Barbados')
# word('Brunei Darussalam')
# word('Bhutan')
# word('Bouvet Island')
# word('Botswana')
# word('Central African Republic')
# word('Canada')
# word('Cocos (Keeling) Islands')
# word('Switzerland')
# word('Chile')
# word('China')
# word('Côte d'Ivoire')
# word('Cameroon')
# word('Congo, The Democratic Republic of the')
# word('Congo')
# word('Cook Islands')
# word('Colombia')
# word('Comoros')
# word('Cabo Verde')
# word('Costa Rica')
# word('Cuba')
# word('Curaçao')
# word('Christmas Island')
# word('Cayman Islands')
# word('Cyprus')
# word('Czechia')
# word('Germany')
# word('Djibouti')
# word('Dominica')
# word('Denmark')
# word('Dominican Republic')
# word('Algeria')
# word('Ecuador')
# word('Egypt')
# word('Eritrea')
# word('Western Sahara')
# word('Spain')
# word('Estonia')
# word('Ethiopia')
# word('Finland')
# word('Fiji')
# word('Falkland Islands (Malvinas)')
# word('France')
# word('Faroe Islands')
# word('Micronesia, Federated States of')
# word('Gabon')
# word('United Kingdom')
# word('Georgia')
# word('Guernsey')
# word('Ghana')
# word('Gibraltar')
# word('Guinea')
# word('Guadeloupe')
# word('Gambia')
# word('Guinea-Bissau')
# word('Equatorial Guinea')
# word('Greece')
# word('Grenada')
# word('Greenland')
# word('Guatemala')
# word('French Guiana')
# word('Guam')
# word('Guyana')
# word('Hong Kong')
# word('Heard Island and McDonald Islands')
# word('Honduras')
# word('Croatia')
# word('Haiti')
# word('Hungary')
# word('Indonesia')
# word('Isle of Man')
# word('India')
# word('British Indian Ocean Territory')
# word('Ireland')
# word('Iran, Islamic Republic of')
# word('Iraq')
# word('Iceland')
# word('Israel')
# word('Italy')
# word('Jamaica')
# word('Jersey')
# word('Jordan')
# word('Japan')
# word('Kazakhstan')
# word('Kenya')
# word('Kyrgyzstan')
# word('Cambodia')
# word('Kiribati')
# word('Saint Kitts and Nevis')
# word('Korea, Republic of')
# word('Kuwait')
# word('Lao People's Democratic Republic')
# word('Lebanon')
# word('Liberia')
# word('Libya')
# word('Saint Lucia')
# word('Liechtenstein')
# word('Sri Lanka')
# word('Lesotho')
# word('Lithuania')
# word('Luxembourg')
# word('Latvia')
# word('Macao')
# word('Saint Martin (French part)')
# word('Morocco')
# word('Monaco')
# word('Moldova, Republic of')
# word('Madagascar')
# word('Maldives')
# word('Mexico')
# word('Marshall Islands')
# word('North Macedonia')
# word('Mali')
# word('Malta')
# word('Myanmar')
# word('Montenegro')
# word('Mongolia')
# word('Northern Mariana Islands')
# word('Mozambique')
# word('Mauritania')
# word('Montserrat')
# word('Martinique')
# word('Mauritius')
# word('Malawi')
# word('Malaysia')
# word('Mayotte')
# word('Namibia')
# word('New Caledonia')
# word('Niger')
# word('Norfolk Island')
# word('Nigeria')
# word('Nicaragua')
# word('Niue')
# word('Netherlands')
# word('Norway')
# word('Nepal')
# word('Nauru')
# word('New Zealand')
# word('Oman')
# word('Pakistan')
# word('Panama')
# word('Pitcairn')
# word('Peru')
# word('Philippines')
# word('Palau')
# word('Papua New Guinea')
# word('Poland')
# word('Puerto Rico')
# word('Korea, Democratic People's Republic of')
# word('Portugal')
# word('Paraguay')
# word('Palestine, State of')
# word('French Polynesia')
# word('Qatar')
# word('Réunion')
# word('Romania')
# word('Russian Federation')
# word('Rwanda')
# word('Saudi Arabia')
# word('Sudan')
# word('Senegal')
# word('Singapore')
# word('South Georgia and the South Sandwich Islands')
# word('Saint Helena, Ascension and Tristan da Cunha')
# word('Svalbard and Jan Mayen')
# word('Solomon Islands')
# word('Sierra Leone')
# word('El Salvador')
# word('San Marino')
# word('Somalia')
# word('Saint Pierre and Miquelon')
# word('Serbia')
# word('South Sudan')
# word('Sao Tome and Principe')
# word('Suriname')
# word('Slovakia')
# word('Slovenia')
# word('Sweden')
# word('Eswatini')
# word('Sint Maarten (Dutch part)')
# word('Seychelles')
# word('Syrian Arab Republic')
# word('Turks and Caicos Islands')
# word('Chad')
# word('Togo')
# word('Thailand')
# word('Tajikistan')
# word('Tokelau')
# word('Turkmenistan')
# word('Timor-Leste')
# word('Tonga')
# word('Trinidad and Tobago')
# word('Tunisia')
# word('Turkey')
# word('Tuvalu')
# word('Taiwan, Province of China')
# word('Tanzania, United Republic of')
# word('Uganda')
# word('Ukraine')
# word('United States Minor Outlying Islands')
# word('Uruguay')
# word('United States')
# word('Uzbekistan')
# word('Holy See (Vatican City State)')
# word('Saint Vincent and the Grenadines')
# word('Venezuela, Bolivarian Republic of')
# word('Virgin Islands, British')
# word('Virgin Islands, U.S.')
# word('Viet Nam')
# word('Vanuatu')
# word('Wallis and Futuna')
# word('Samoa')
# word('Yemen')
# word('South Africa')
# word('Zambia')
# word('Zimbabwe')


def countries_list():
    """Return a list of countries sorted by name, suitable for use in a multiple-choice field.

    Each element in the list is a single-key dictionary mapping the two-letter
    ISO 3166-1 alpha-2 country code to the country name.

    Returns:
        list: A list of dicts, each mapping a country code (str) to a country name (str).
    """
    return [{item[0]: item[1]} for item in sorted([[country.alpha_2, word(country.name)] for country in pycountry.countries], key=lambda x: x[1])]


def states_list(country_code=None, abbreviate=False):
    """Return a dictionary of state or subdivision abbreviations to full names.

    Returns the first-level subdivisions of the given country, sorted by name,
    suitable for use in a multiple-choice field.

    Args:
        country_code (str, optional): A two-letter ISO 3166-1 alpha-2 country
            code. Defaults to the current country as returned by ``get_country()``.
        abbreviate (bool, optional): If True, both keys and values will be the
            abbreviated subdivision code. Defaults to False.

    Returns:
        dict: A dictionary mapping subdivision abbreviations to full names,
            or abbreviations to abbreviations if ``abbreviate=True``.
    """
    ensure_definition(country_code)
    if country_code is None:
        country_code = get_country() or 'US'
    mapping = {}
    state_list = pycountry.subdivisions.get(country_code=country_code)
    if state_list is None:
        return {}
    for subdivision in state_list:
        if subdivision.parent_code is not None:
            continue
        m = re.search(r'-([A-Z0-9]+)$', subdivision.code)
        if m:
            if abbreviate:
                mapping[m.group(1)] = m.group(1)
            else:
                mapping[m.group(1)] = word(subdivision.name)
    return dict(sorted(mapping.items(), key=lambda item: item[1]))


def interface():
    """Return a string describing how the interview is being accessed.

    Possible return values are ``'web'`` (browser), ``'json'`` (web with JSON
    parameter), ``'api'`` (REST API), ``'sms'`` (SMS/text message), ``'cron'``
    (scheduled task), or ``'worker'`` (background process).

    Returns:
        str: The interface type, or None if unknown.
    """
    return this_thread.current_info.get('interface', None)


def user_privileges():
    """Return a list of the current user's privileges.

    For users who are not logged in, this is always ``['user']``. For
    scheduled tasks, this is ``['cron']``.

    Returns:
        list: A list of privilege strings (e.g., ``['user', 'admin']``).
    """
    if user_logged_in():
        return list(this_thread.current_info['user']['roles'])
    return ['user']


def user_has_privilege(*pargs):
    """Return True if the current user has any of the given privileges.

    Args:
        *pargs: One or more privilege names (strings) or lists of privilege
            names. Returns True if the user holds any of the named privileges.

    Returns:
        bool: True if the user has at least one of the specified privileges,
            False otherwise.
    """
    privileges = []
    for parg in pargs:
        if isinstance(parg, list):
            arg_list = parg
        elif isinstance(parg, str):
            arg_list = [parg]
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')) or isinstance(parg, Iterable):
            arg_list = []
            for sub_parg in parg:
                arg_list.append(str(sub_parg))
        else:
            arg_list = [parg]
        for arg in arg_list:
            privileges.append(arg)
    if user_logged_in():
        for privilege in privileges:
            if privilege in this_thread.current_info['user']['roles']:
                return True
    else:
        if 'user' in privileges:
            return True
    return False


class AttachmentInfo:
    pass


class TheContext:

    @property
    def session(self):
        return get_uid()

    @property
    def filename(self):
        return this_thread.current_info.get('yaml_filename', None)

    @property
    def package(self):
        filename = this_thread.current_info.get('yaml_filename', None)
        if filename:
            return re.sub(r':.*', '', filename)
        return None

    @property
    def question_id(self):
        try:
            return this_thread.current_question.id
        except:
            return None

    @property
    def variable(self):
        try:
            return this_thread.current_variable[-1]
        except:
            return None

    @property
    def current_package(self):
        try:
            return this_thread.current_question.from_source.package
        except:
            return None

    @property
    def current_filename(self):
        try:
            return this_thread.current_question.from_source.path
        except:
            return None

    @property
    def current_section(self):
        try:
            return this_thread.current_section or get_user_dict()['nav'].current
        except:
            return None

    @property
    def inside_of(self):
        try:
            return this_thread.evaluation_context or 'standard'
        except:
            return 'standard'

    @property
    def request_url(self):
        try:
            info = server.get_url()
        except:
            info = {}
        return info

    @property
    def attachment(self):
        info = AttachmentInfo()
        if 'attachment_info' in this_thread.misc:
            info.name = this_thread.misc['attachment_info'].get('name', '')
            info.filename = this_thread.misc['attachment_info'].get('filename', '')
            info.description = this_thread.misc['attachment_info'].get('description', '')
            info.update_references = bool(this_thread.misc['attachment_info'].get('update_references', False))
            info.redact = this_thread.misc.get('redact', True)
            info.pdfa = bool(this_thread.misc['attachment_info'].get('convert_to_pdf_a', False))
            info.tagged = bool(this_thread.misc['attachment_info'].get('convert_to_tagged_pdf', False))
        else:
            info.name = ''
            info.filename = ''
            info.description = ''
            info.update_references = False
            info.redact = True
            info.pdfa = False
            info.tagged = False
        return info


warnings_given = {}


def warn_if_not_warned(the_function, the_attribute, alternate_function):
    if the_function not in warnings_given:
        warnings_given[the_function] = set()
    if the_attribute in warnings_given[the_function]:
        return
    logmessage("DEPRECATION WARNING: in a future version, the " + the_function + "() function will not support the attribute " + the_attribute + ". Use " + alternate_function + "()." + the_attribute + " instead.")
    warnings_given[the_function].add(the_attribute)


class TheUser:

    def name(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name
        if self.last_name:
            return self.last_name
        if self.first_name:
            return self.first_name
        return word("Unnamed User")

    @property
    def first_name(self):
        if user_logged_in():
            return this_thread.current_info['user']['firstname']
        return word("Anonymous")

    @property
    def last_name(self):
        if user_logged_in():
            return this_thread.current_info['user']['lastname']
        return word("User")

    @property
    def id(self):
        if user_logged_in():
            return this_thread.current_info['user']['theid']
        return None

    @property
    def login_method(self):
        if user_logged_in():
            return this_thread.current_info['user']['login_method']
        return None

    @property
    def phone_number(self):
        if user_logged_in() and this_thread.current_info['user']['login_method'] == 'phone':
            return this_thread.current_info['user']['nickname']
        return None

    @property
    def email(self):
        if user_logged_in():
            return this_thread.current_info['user']['email']
        return None

    @property
    def country(self):
        if user_logged_in():
            return this_thread.current_info['user']['country']
        return None

    @property
    def subdivision_first(self):
        if user_logged_in():
            return this_thread.current_info['user']['subdivisionfirst']
        return None

    @property
    def subdivision_second(self):
        if user_logged_in():
            return this_thread.current_info['user']['subdivisionsecond']
        return None

    @property
    def subdivision_third(self):
        if user_logged_in():
            return this_thread.current_info['user']['subdivisionthird']
        return None

    @property
    def organization(self):
        if user_logged_in():
            return this_thread.current_info['user']['organization']
        return None

    @property
    def language(self):
        if user_logged_in():
            return this_thread.current_info['user']['language']
        return None

    @property
    def timezone(self):
        if user_logged_in():
            return this_thread.current_info['user']['timezone']
        return None

    @property
    def privileges(self):
        return user_privileges()

    @property
    def permissions(self):
        enabled_privileges = set()
        for privilege in user_privileges():
            enabled_privileges.update(server.get_permissions_of_privilege(privilege, privileged=True))
        return list(enabled_privileges)

    @property
    def session(self):
        warn_if_not_warned('user_info', 'session', 'current_context')
        return get_uid()

    @property
    def filename(self):
        warn_if_not_warned('user_info', 'filename', 'current_context')
        return this_thread.current_info.get('yaml_filename', None)

    @property
    def package(self):
        warn_if_not_warned('user_info', 'package', 'current_context')
        filename = this_thread.current_info.get('yaml_filename', None)
        if filename:
            return re.sub(r':.*', '', filename)
        return None

    @property
    def question_id(self):
        warn_if_not_warned('user_info', 'question_id', 'current_context')
        try:
            return this_thread.current_question.id
        except:
            return None

    @property
    def variable(self):
        warn_if_not_warned('user_info', 'variable', 'current_context')
        try:
            return this_thread.current_variable[-1]
        except:
            return None

    @property
    def current_package(self):
        warn_if_not_warned('user_info', 'current_package', 'current_context')
        try:
            return this_thread.current_question.from_source.package
        except:
            return None

    @property
    def current_filename(self):
        warn_if_not_warned('user_info', 'current_filename', 'current_context')
        try:
            return this_thread.current_question.from_source.path
        except:
            return None

    @property
    def current_section(self):
        warn_if_not_warned('user_info', 'current_section', 'current_context')
        try:
            return this_thread.current_section or get_user_dict()['nav'].current
        except:
            return None

    def __str__(self):
        return str(self.name())


def current_context():
    """Return an object describing the context in which Python code is executing.

    The returned object has attributes including ``session``, ``filename``,
    ``package``, ``question_id``, ``current_filename``, ``current_package``,
    ``variable``, ``current_section``, ``inside_of``, ``attachment``, and
    ``request_url``.

    Returns:
        TheContext: An object with context attributes for the current execution.
    """
    return TheContext()


def user_info():
    """Return an object with information about the current user's profile.

    The returned object has attributes including ``id``, ``first_name``,
    ``last_name``, ``email``, ``login_method``, ``phone_number``, ``country``,
    ``subdivision_first``, ``subdivision_second``, ``subdivision_third``,
    ``organization``, ``language``, ``timezone``, and ``privileges``.

    Returns:
        TheUser: An object with attributes describing the current user.
    """
    return TheUser()


def action_arguments():
    """Return a dictionary of arguments passed to the current action.

    Used when processing an action triggered by ``url_action()`` or
    ``interview_url_action()``. The special keys ``_initial`` and ``_changed``
    are excluded from the result.

    Returns:
        dict: A dictionary of keyword arguments passed to the action, or an
            empty dictionary if no arguments were provided.
    """
    if 'arguments' in this_thread.current_info:
        args = copy.deepcopy(this_thread.current_info['arguments'])
        if '_initial' in args and '_changed' in args:
            del args['_initial']
            del args['_changed']
        return args
    return {}


def action_argument(item=None):
    """Return the value of a named argument for the current action.

    Used when processing an action triggered by ``url_action()`` or
    ``interview_url_action()``. If called without an argument, returns the
    name of the action itself (useful in ``initial`` blocks before calling
    ``process_action()``). Returns None if no action is active.

    Args:
        item (str, optional): The name of the argument to retrieve. If omitted,
            the name of the action itself is returned. Defaults to None.

    Returns:
        The value of the specified argument, the action name (if ``item`` is
            None), or None if the action or argument is not found.
    """
    # logmessage("action_argument: item is " + str(item) + " and arguments are " + repr(this_thread.current_info['arguments']))
    if item is None:
        return this_thread.current_info.get('action', None)
    if 'arguments' in this_thread.current_info:
        return this_thread.current_info['arguments'].get(item, None)
    return None


def location_returned():
    """Return True if an attempt has been made to transmit the user's GPS location.

    Returns True even if the attempt was unsuccessful or the user refused to
    consent to the transfer. Use ``location_known()`` to test whether the
    location was successfully obtained.

    Returns:
        bool: True if a location transmission has been attempted, False otherwise.
    """
    # logmessage("Location returned")
    if 'user' in this_thread.current_info:
        # logmessage("user exists")
        if 'location' in this_thread.current_info['user']:
            # logmessage("location exists")
            # logmessage("Type is " + str(type(this_thread.current_info['user']['location'])))
            pass
    return bool('user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and isinstance(this_thread.current_info['user']['location'], dict))


def location_known():
    """Return True if docassemble successfully obtained the user's GPS location.

    Returns:
        bool: True if the user's latitude and longitude are known, False otherwise.
    """
    return bool('user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and isinstance(this_thread.current_info['user']['location'], dict) and 'latitude' in this_thread.current_info['user']['location'])


def user_lat_lon():
    """Return the user's latitude and longitude as a tuple.

    Returns:
        tuple: A ``(latitude, longitude)`` tuple of floats if the location is
            known, or ``(None, None)`` if the location is not available. If
            there was a location error, returns ``(error_message, error_message)``.
    """
    if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and isinstance(this_thread.current_info['user']['location'], dict):
        if 'latitude' in this_thread.current_info['user']['location'] and 'longitude' in this_thread.current_info['user']['location']:
            return this_thread.current_info['user']['location']['latitude'], this_thread.current_info['user']['location']['longitude']
        if 'error' in this_thread.current_info['user']['location']:
            return this_thread.current_info['user']['location']['error'], this_thread.current_info['user']['location']['error']
    return None, None


def chat_partners_available(*pargs, **kwargs):
    """Return the number of chat partners available to the user.

    Args:
        *pargs: One or more partner role names (strings or lists of strings)
            to include as valid chat partners.
        partner_roles (list, optional): Additional partner roles. Defaults to [].
        mode (str, optional): The chat mode, e.g., ``'peerhelp'``. Defaults to
            ``'peerhelp'``.

    Returns:
        dict: A dictionary with keys ``'peer'`` and ``'help'``, each mapping to
            an integer count of available partners.
    """
    partner_roles = kwargs.get('partner_roles', [])
    mode = kwargs.get('mode', 'peerhelp')
    if not isinstance(partner_roles, list):
        partner_roles = [partner_roles]
    for parg in pargs:
        if isinstance(parg, list):
            the_parg = parg
        elif isinstance(parg, str):
            the_parg = [parg]
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')) or isinstance(parg, Iterable):
            the_parg = []
            for sub_parg in parg:
                the_parg.append(str(sub_parg))
        else:
            the_parg = [parg]
        for the_arg in the_parg:
            if the_arg not in partner_roles:
                partner_roles.append(the_arg)
    yaml_filename = this_thread.current_info['yaml_filename']
    session_id = this_thread.current_info['session']
    if this_thread.current_info['user']['is_authenticated']:
        the_user_id = this_thread.current_info['user']['theid']
    else:
        the_user_id = 't' + str(this_thread.current_info['user']['theid'])
    if the_user_id == 'tNone':
        logmessage("chat_partners_available: unable to get temporary user id")
        return {'peer': 0, 'help': 0}
    return server.chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles)


def interview_email(key=None, index=None):
    """Return an e-mail address that routes incoming messages to this interview session.

    The address is a unique random identifier at the configured incoming mail
    domain. Every call with the same ``key`` and ``index`` returns the same address.

    Args:
        key (str, optional): A label to distinguish different e-mail addresses
            for the same session (e.g., ``'evidence'``, ``'opposing counsel'``).
            Defaults to None.
        index (int, optional): An integer to further distinguish addresses under
            the same ``key``. Requires ``key`` to be set. Defaults to None.

    Returns:
        str: An e-mail address string (e.g., ``'kgjeir@help.example.com'``).
    """
    if key is None and index is not None:
        raise DAError("interview_email: if you provide an index you must provide a key")
    domain = server.daconfig.get('incoming mail domain', server.daconfig.get('external hostname', server.hostname))
    return server.get_short_code(key=key, index=index) + '@' + domain


def get_emails(key=None, index=None):
    """Return information about e-mail addresses and messages for this interview session.

    Returns a list of objects, each with attributes ``address``, ``emails``,
    ``key``, and ``index``.

    Args:
        key (str, optional): Filter results to addresses created with this key.
            Defaults to None (returns all addresses).
        index (int, optional): Further filter to the address with this index
            under the given ``key``. Defaults to None.

    Returns:
        list: A list of objects representing e-mail addresses and their received
            messages.
    """
    return server.retrieve_emails(key=key, index=index)


def modify_i_argument(args):
    if 'i' not in args:
        return
    if not isinstance(args['i'], str):
        args['i'] = str(args['i'])
    if args['i'].startswith('docassemble.'):
        return
    args['i'] = re.sub(r'^data/questions/', '', args['i'])
    try:
        args['i'] = get_current_question().package + ':data/questions/' + args['i']
    except:
        try:
            args['i'] = this_thread.current_package + ':data/questions/' + args['i']
        except:
            pass


def interview_url(**kwargs):
    """Return a URL that links directly to the current interview session.

    Used in multi-user interviews to invite additional users to participate.
    Keyword arguments are included as URL parameters. Special keyword arguments
    include ``i`` (interview filename), ``session`` (session ID), ``local``
    (return a relative URL), ``new_session``, ``reset``, ``style``,
    ``temporary`` (expire in N hours), and ``once_temporary``.

    Returns:
        str: A URL string pointing to the interview session.
    """
    do_local = False
    args = {}
    temporary = kwargs.pop('temporary', None)
    once_temporary = kwargs.pop('once_temporary', None)
    for key, val in kwargs.items():
        args[key] = val
    if 'local' in args:
        if args['local']:
            do_local = True
        del args['local']
    if 'i' in args:
        if 'session' not in args:
            args['from_list'] = 1
        if not isinstance(args['i'], str):
            args['i'] = str(args['i'])
    else:
        args['i'] = this_thread.current_info['yaml_filename']
        if not args.get('session', None):
            args['session'] = this_thread.current_info['session']
    modify_i_argument(args)
    if not do_local:
        args['_external'] = True
    try:
        if int(args['new_session']):
            del args['session']
    except:
        pass
    if 'style' in args and args['style'] in ('short', 'short_package'):
        the_style = args['style']
        del args['style']
        is_new = False
        try:
            if int(args['new_session']):
                is_new = True
                del args['new_session']
        except:
            is_new = False
        url = None
        if the_style == 'short':
            for k, v in server.daconfig.get('dispatch').items():
                if v == args['i']:
                    args['dispatch'] = k
                    del args['i']
                    if is_new:
                        url = url_of('run_new_dispatch', **args)
                    else:
                        url = url_of('run_dispatch', **args)
                    break
        if url is None:
            package, filename = re.split(r':', args['i'])
            package = re.sub(r'^docassemble\.', '', package)
            filename = re.sub(r'^data/questions/', '', filename)
            filename = re.sub(r'.yml$', '', filename)
            args['package'] = package
            args['filename'] = filename
            del args['i']
            if is_new:
                url = url_of('run_new', **args)
            else:
                url = url_of('run', **args)
    elif 'style' not in args and args['i'] == this_thread.current_info['yaml_filename']:
        url = url_of('flex_interview', **args)
    else:
        url = url_of('interview', **args)
    if temporary:
        if isinstance(temporary, (int, float)) and temporary > 0:
            expire_seconds = int(temporary * 60 * 60)
        else:
            expire_seconds = 24 * 60 * 60
        return temp_redirect(url, expire_seconds, do_local, False)
    if once_temporary in args:
        if isinstance(once_temporary, (int, float)) and once_temporary > 0:
            expire_seconds = int(once_temporary * 60 * 60)
        else:
            expire_seconds = 24 * 60 * 60
        return temp_redirect(url, expire_seconds, do_local, True)
    return url


def temp_redirect(url, expire_seconds, do_local, one_time):
    while True:
        code = random_string(32)
        the_key = 'da:temporary_url:' + code
        if server.server_redis.get(the_key) is None:
            break
    pipe = server.server_redis.pipeline()
    if one_time:
        pipe.set(the_key, json.dumps({'url': url, 'once': True}))
    else:
        pipe.set(the_key, json.dumps({'url': url}))
    pipe.expire(the_key, expire_seconds)
    pipe.execute()
    if do_local:
        return server.url_for('run_temp', c=code)
    return server.url_for('run_temp', c=code, _external=True)


def set_parts(**kwargs):
    """Set parts of the page display, such as the title, navigation bar text, and HTML.

    Keyword arguments correspond to page part names. Recognized keywords include
    ``title``, ``short``, ``tab``, ``subtitle``, ``logo``, ``exit link``,
    ``exit label``, ``pre``, ``post``, ``submit``, ``continue button label``,
    ``help label``, ``under``, ``right``, ``footer``, and others.
    """
    if 'short' in kwargs:
        this_thread.internal['short title'] = kwargs['short']
    if 'tab' in kwargs:
        this_thread.internal['tab title'] = kwargs['tab']
    if 'subtitle' in kwargs:
        this_thread.internal['subtitle'] = kwargs['subtitle']
    for key, val in kwargs.items():
        key = re.sub(r'_', r' ', key)
        if key in ('title', 'logo', 'exit link', 'exit label', 'exit url', 'pre', 'post', 'submit', 'continue button label', 'help label', 'under', 'right', 'tab title', 'short title', 'short logo', 'back button label', 'corner back button label', 'resume button label', 'date format', 'time format', 'datetime format', 'footer', 'title url', 'css class', 'table css class', 'title url opens in other window', 'navigation bar html'):
            this_thread.internal[key] = val


def set_title(**kwargs):
    """Set parts of the page display (deprecated; use ``set_parts()`` instead)."""
    logmessage("warning: the set_title() function has been renamed to set_parts()")
    return set_parts(**kwargs)


class DATagsSet():

    def add(self, item):
        """Adds the item to the set"""
        this_thread.internal['tags'].add(item)

    def copy(self):
        """Returns a copy of the set."""
        return this_thread.internal['tags'].copy()

    def clear(self):
        """Removes all the items from the set."""
        this_thread.internal['tags'] = set()

    def remove(self, elem):
        """Removes an element from the set."""
        this_thread.internal['tags'].remove(elem)

    def discard(self, elem):
        """Removes an element from the set if it exists."""
        this_thread.internal['tags'].discard(elem)

    def pop(self, *pargs):
        """Remove and return an arbitrary element from the set"""
        return this_thread.internal['tags'].pop(*pargs)

    def __contains__(self, item):
        return this_thread.internal['tags'].__contains__(item)

    def __iter__(self):
        return this_thread.internal['tags'].__iter__()

    def __len__(self):
        return this_thread.internal['tags'].__len__()

    def __reversed__(self):
        return this_thread.internal['tags'].__reversed__()

    def __and__(self, operand):
        return this_thread.internal['tags'].__and__(operand)

    def __or__(self, operand):
        return this_thread.internal['tags'].__or__(operand)

    def __iand__(self, operand):
        return this_thread.internal['tags'].__iand__(operand)

    def __ior__(self, operand):
        return this_thread.internal['tags'].__ior__(operand)

    def __isub__(self, operand):
        return this_thread.internal['tags'].__isub__(operand)

    def __ixor__(self, operand):
        return this_thread.internal['tags'].__ixor__(operand)

    def __rand__(self, operand):
        return this_thread.internal['tags'].__rand__(operand)

    def __ror__(self, operand):
        return this_thread.internal['tags'].__ror__(operand)

    def __hash__(self):
        return this_thread.internal['tags'].__hash__()

    def __str__(self):
        return str(this_thread.internal['tags'])

    def union(self, other_set):
        """Returns a Python set consisting of the elements of current set
        combined with the elements of the other_set.

        """
        return this_thread.internal['tags'].union(other_set)

    def intersection(self, other_set):
        """Returns a Python set consisting of the elements of the current set
        that also exist in the other_set.

        """
        return this_thread.internal['tags'].intersection(other_set)

    def difference(self, other_set):
        """Returns a Python set consisting of the elements of the current set
        that do not exist in the other_set.

        """
        return this_thread.internal['tags'].difference(other_set)

    def isdisjoint(self, other_set):
        """Returns True if no elements overlap between the current set and the
        other_set.  Otherwise, returns False."""
        return this_thread.internal['tags'].isdisjoint(other_set)

    def issubset(self, other_set):
        """Returns True if the current set is a subset of the other_set.
        Otherwise, returns False.

        """
        return this_thread.internal['tags'].issubset(other_set)

    def issuperset(self, other_set):
        """Returns True if the other_set is a subset of the current set.
        Otherwise, returns False.

        """
        return this_thread.internal['tags'].issuperset(other_set)


def session_tags():
    """Return the set of tags associated with the current interview session.

    The tags are initialized from the ``tags`` list in any ``metadata`` blocks
    and can be modified using the returned set object.

    Returns:
        DATagsSet: A set-like object containing the current session tags.
    """
    if 'tags' not in this_thread.internal:
        this_thread.internal['tags'] = set()
        for metadata in this_thread.interview.metadata:
            if 'tags' in metadata and isinstance(metadata['tags'], list):
                for tag in metadata['tags']:
                    this_thread.internal['tags'].add(tag)
    return DATagsSet()


def interview_path():
    try:
        return this_thread.interview.source.path
    except:
        return None


def interview_url_action(action, **kwargs):
    """Return a URL that links to the interview and triggers a specified action.

    Like ``interview_url()``, but additionally encodes an action to run when
    the URL is visited. Keyword arguments are passed as action arguments, except
    for ``i``, ``session``, ``local``, ``new_session``, ``reset``,
    ``_forget_prior``, ``style``, ``temporary``, and ``once_temporary``, which
    control the URL behavior.

    Args:
        action (str): The name of the action to trigger.
        **kwargs: Arguments to the action and URL modifiers.

    Returns:
        str: A URL string that will trigger the specified action when visited.
    """
    do_local = False
    if 'local' in kwargs:
        if kwargs['local']:
            do_local = True
        del kwargs['local']
    args = {}
    if 'i' in kwargs:
        if kwargs['i']:
            args['i'] = kwargs['i']
        else:
            args['i'] = this_thread.current_info['yaml_filename']
        del kwargs['i']
    else:
        args['i'] = this_thread.current_info['yaml_filename']
    modify_i_argument(args)
    if 'new_session' in kwargs:
        if kwargs['new_session']:
            args['new_session'] = '1'
        del kwargs['new_session']
    if 'reset' in kwargs:
        if kwargs['reset']:
            args['reset'] = '1'
        del kwargs['reset']
    if 'session' in kwargs:
        if kwargs['session']:
            args['session'] = kwargs['session']
        del kwargs['session']
    elif args['i'] == this_thread.current_info['yaml_filename']:
        args['session'] = this_thread.current_info['session']
    if contains_volatile.search(action):
        raise DAError("interview_url_action cannot be used with a generic object or a variable iterator")
    if 'style' in kwargs and kwargs['style'] in ('short', 'short_package'):
        args['style'] = kwargs['style']
        del kwargs['style']
    if '_forget_prior' in kwargs:
        is_priority = bool(kwargs['_forget_prior'])
        del kwargs['_forget_prior']
        if is_priority:
            kwargs = {'_action': action, '_arguments': kwargs}
            action = '_da_priority_action'
    temporary = kwargs.pop('temporary', None)
    once_temporary = kwargs.pop('once_temporary', None)
    args['action'] = myb64quote(json.dumps({'action': action, 'arguments': kwargs}))
    if not do_local:
        args['_external'] = True
    try:
        if int(args['new_session']):
            del args['session']
    except:
        pass
    if 'style' in args and args['style'] in ('short', 'short_package'):
        the_style = args['style']
        del args['style']
        is_new = False
        try:
            if int(args['new_session']):
                is_new = True
                del args['new_session']
        except:
            pass
        url = None
        if the_style == 'short':
            for k, v in server.daconfig.get('dispatch').items():
                if v == args['i']:
                    args['dispatch'] = k
                    del args['i']
                    if is_new:
                        url = url_of('run_new_dispatch', **args)
                    else:
                        url = url_of('run_dispatch', **args)
                    break
        if url is None:
            package, filename = re.split(r':', args['i'])
            package = re.sub(r'^docassemble\.', '', package)
            filename = re.sub(r'^data/questions/', '', filename)
            filename = re.sub(r'.yml$', '', filename)
            args['package'] = package
            args['filename'] = filename
            del args['i']
            if is_new:
                url = url_of('run_new', **args)
            else:
                url = url_of('run', **args)
    elif 'style' not in args and args['i'] == this_thread.current_info['yaml_filename']:
        url = url_of('flex_interview', **args)
    else:
        url = url_of('interview', **args)
    if temporary is not None:
        if isinstance(temporary, (int, float)) and temporary > 0:
            expire_seconds = int(temporary * 60 * 60)
        else:
            expire_seconds = 24 * 60 * 60
        return temp_redirect(url, expire_seconds, do_local, False)
    if once_temporary is not None:
        if isinstance(once_temporary, (int, float)) and once_temporary > 0:
            expire_seconds = int(once_temporary * 60 * 60)
        else:
            expire_seconds = 24 * 60 * 60
        return temp_redirect(url, expire_seconds, do_local, True)
    return url


def interview_url_as_qr(**kwargs):
    """Return markup for a QR code linking to the current interview session.

    Can be used to pass control from a web browser or a paper handout to a
    mobile device. Accepts the same keyword arguments as ``interview_url()``,
    plus ``alt_text`` and ``width`` for the QR code image.

    Returns:
        str: Markup string containing a QR code image linking to the interview.
    """
    alt_text = None
    width = None
    the_kwargs = {}
    for key, val in kwargs.items():
        if key == 'alt_text':
            alt_text = val
        elif key == 'width':
            width = val
        else:
            the_kwargs[key] = val
    return qr_code(interview_url(**the_kwargs), alt_text=alt_text, width=width)


def interview_url_action_as_qr(action, **kwargs):
    """Return markup for a QR code linking to the interview with a specified action.

    Like ``interview_url_as_qr()``, but the URL encodes an action to run when
    visited. Accepts the same keyword arguments as ``interview_url_action()``,
    plus ``alt_text`` and ``width`` for the QR code image.

    Args:
        action (str): The name of the action to trigger when the QR code is scanned.
        **kwargs: Arguments to the action and URL/image modifiers.

    Returns:
        str: Markup string containing a QR code image linking to the action URL.
    """
    alt_text = None
    width = None
    the_kwargs = {}
    for key, val in kwargs.items():
        if key == 'alt_text':
            alt_text = val
        elif key == 'width':
            width = val
        else:
            the_kwargs[key] = val
    return qr_code(interview_url_action(action, **the_kwargs), alt_text=alt_text, width=width)


def get_info(att):
    """Return the value of a global variable previously set with ``set_info()``.

    Args:
        att (str): The name of the attribute to retrieve.

    Returns:
        The value that was set for the attribute, or None if it was never set.
    """
    if hasattr(this_thread.global_vars, att):
        return getattr(this_thread.global_vars, att)
    return None


def get_current_info():
    return this_thread.current_info


def set_info(**kwargs):
    """Store global variables for later retrieval with ``get_info()``.

    Typically called in an ``initial`` code block so the values are refreshed
    on every page load. Common usage includes setting ``user`` and ``role``.

    Args:
        **kwargs: Keyword arguments whose names become attribute names and
            whose values are stored for later retrieval.
    """
    for att, val in kwargs.items():
        setattr(this_thread.global_vars, att, val)


def set_progress(number):
    """Set the position of the interview progress meter.

    Args:
        number (int or float): The progress value to display. Pass None to
            hide the progress meter.
    """
    this_thread.internal['progress'] = number


def get_progress():
    """Return the current value of the interview progress meter.

    Returns:
        int or float: The current progress value.
    """
    return this_thread.internal['progress']


def update_terms(dictionary, auto=False, language='*'):
    """Define or override interview-wide terms or auto terms programmatically.

    Args:
        dictionary (dict or list): A dictionary mapping term strings to their
            definitions, or a list of single-key dictionaries.
        auto (bool, optional): If True, update ``auto terms`` instead of
            ``terms``. Defaults to False.
        language (str, optional): The language code for which to set the terms.
            Use ``'*'`` for the default language. Defaults to ``'*'``.
    """
    if auto:
        type_of_term = 'autoterms'
    else:
        type_of_term = 'terms'
    if type_of_term not in this_thread.internal:
        this_thread.internal[type_of_term] = {}
    if language not in this_thread.internal[type_of_term]:
        this_thread.internal[type_of_term][language] = {}
    terms = this_thread.internal[type_of_term][language]
    if isinstance(dictionary, list):
        for termitem in dictionary:
            if isinstance(termitem, dict):
                if len(termitem) == 2 and 'phrases' in termitem and isinstance(termitem['phrases'], list) and 'definition' in termitem:
                    termitems = [(phrase, termitem['definition']) for phrase in termitem['phrases']]
                else:
                    termitems = termitem.items()
                for term, definition in termitems:
                    lower_term = re.sub(r'\s+', ' ', term.lower())
                    if auto:
                        terms[lower_term] = {'definition': str(definition), 're': re.compile(r"(?i){?\b(%s)\b}?" % (re.sub(r'\s', r'\\s+', lower_term),), re.IGNORECASE | re.DOTALL)}  # noqa: W605
                    else:
                        terms[lower_term] = {'definition': str(definition), 're': re.compile(r"(?i){(%s)(\|[^\}]*)?}" % (re.sub(r'\s', r'\\s+', lower_term),), re.IGNORECASE | re.DOTALL)}  # noqa: W605
            else:
                raise DAError("update_terms: terms organized as a list must be a list of dictionary items.")
    elif isinstance(dictionary, dict):
        for term in dictionary:
            lower_term = re.sub(r'\s+', ' ', term.lower())
            if auto:
                terms[lower_term] = {'definition': str(dictionary[term]), 're': re.compile(r"(?i){?\b(%s)\b}?" % (re.sub(r'\s', r'\\s+', lower_term),), re.IGNORECASE | re.DOTALL)}  # noqa: W605
            else:
                terms[lower_term] = {'definition': str(dictionary[term]), 're': re.compile(r"(?i){(%s)(\|[^\}]*)?}" % (re.sub(r'\s', r'\\s+', lower_term),), re.IGNORECASE | re.DOTALL)}  # noqa: W605
    else:
        raise DAError("update_terms: terms must be organized as a dictionary or a list.")


def set_save_status(status):
    """Control whether the current interview logic processing creates a new step.

    Args:
        status (str): One of ``'new'`` (create a new step, the default),
            ``'overwrite'`` (overwrite the current step), or ``'ignore'``
            (do not save a new step at all).
    """
    if status in ('new', 'overwrite', 'ignore'):
        if this_thread.misc.get('save_status', SS_NEW) == SS_IGNORE:
            if status != 'ignore':
                logmessage("Call to set_save_status disregarded because save status was already 'ignore'")
        else:
            if status == 'new':
                this_thread.misc['save_status'] = SS_NEW
            if status == 'overwrite':
                this_thread.misc['save_status'] = SS_OVERWRITE
            if status == 'ignore':
                this_thread.misc['save_status'] = SS_IGNORE
                server.release_lock(this_thread.current_info['session'], this_thread.current_info['yaml_filename'])


class DANav:

    def __init__(self):
        self.past = set()
        self.sections = None
        self.current = None
        self.progressive = True
        self.hidden = False
        self.disabled = False

    def __str__(self):
        return self.show_sections()

    def set_section(self, section):
        """Sets the current section in the navigation."""
        if section == self.current:
            return False
        self.current = section
        self.past.add(section)
        return True

    def section_ids(self, language=None):
        """Returns a list of section names or section IDs."""
        the_sections = self.get_sections(language=language)
        all_ids = []
        for x in the_sections:
            subitems = None
            if isinstance(x, dict):
                if len(x) == 2 and 'subsections' in x:
                    for key, val in x.items():
                        if key == 'subsections':
                            subitems = val
                        else:
                            all_ids.append(key)
                elif len(x) == 1:
                    the_key = list(x)[0]
                    the_value = x[the_key]
                    if isinstance(the_value, list):
                        subitems = the_value
                    all_ids.append(the_key)
                else:
                    logmessage("navigation_bar: too many keys in dict.  " + repr(the_sections))
                    continue
            else:
                all_ids.append(str(x))
            if subitems:
                for y in subitems:
                    if isinstance(y, dict):
                        if len(y) == 1:
                            all_ids.append(list(y)[0])
                        else:
                            logmessage("navigation_bar: too many keys in dict.  " + repr(the_sections))
                            continue
                    else:
                        all_ids.append(str(y))
        return all_ids

    def get_section(self, display=False, language=None):
        """Returns the current section of the navigation."""
        current_section = self.current
        if current_section is None or not display:
            return current_section
        the_sections = self.get_sections(language=language)
        current_title = current_section
        for x in the_sections:
            subitems = None
            if isinstance(x, dict):
                if len(x) == 2 and 'subsections' in x:
                    for key, val in x.items():
                        if key == 'subsections':
                            subitems = val
                        else:
                            the_key = key
                            the_title = val
                elif len(x) == 1:
                    the_key = list(x)[0]
                    the_value = x[the_key]
                    if isinstance(the_value, list):
                        subitems = the_value
                        the_title = the_key
                    else:
                        the_title = the_value
                else:
                    logmessage("navigation_bar: too many keys in dict.  " + repr(the_sections))
                    continue
            else:
                the_key = None
                the_title = str(x)
            if (the_key is not None and current_section == the_key) or (the_key is None and current_section == the_title):
                current_title = the_title
                break
            if subitems:
                found_it = False
                for y in subitems:
                    if isinstance(y, dict):
                        if len(y) == 1:
                            sub_key = list(y)[0]
                            sub_title = y[sub_key]
                        else:
                            logmessage("navigation_bar: too many keys in dict.  " + repr(the_sections))
                            continue
                    else:
                        sub_key = None
                        sub_title = str(y)
                    if (sub_key is not None and current_section == sub_key) or (sub_key is None and current_section == sub_title):
                        current_title = sub_title
                        found_it = True
                        break
                if found_it:
                    break
        return current_title

    def hide(self):
        """Hides the navigation bar, except if it is displayed inline."""
        self.hidden = True

    def unhide(self):
        """Unhides the navigation bar if it was hidden."""
        self.hidden = False

    def disable(self):
        """Disabled clickable links in the navigation bar."""
        self.disabled = True

    def enable(self):
        """Enables clickable links in the navigation bar, if links had been disabled."""
        self.disabled = False

    def visible(self, language=None):
        """Returns False if the navigation bar is hidden, and True otherwise."""
        if self.sections is None or len(self.get_sections(language=language)) == 0:
            return False
        return not (hasattr(self, 'hidden') and self.hidden)

    def enabled(self):
        """Returns False if clickable links in the navigation bar are disabled, and True otherwise."""
        return not (hasattr(self, 'disabled') and self.disabled)

    def set_sections(self, sections, language=None):
        """Sets the sections of the navigation to the given list."""
        if language is None:
            language = this_thread.language
        if sections is None:
            sections = []
        if self.sections is None:
            self.sections = {}
        self.sections[language] = sections

    def get_sections(self, language=None):
        """Returns the sections of the navigation as a list."""
        if language is None:
            language = this_thread.language
        if language not in self.sections:
            language = '*'
        return self.sections.get(language, [])

    def show_sections(self, style='inline', show_links=None):
        """Returns the sections of the navigation as HTML."""
        if show_links is None:
            if hasattr(self, 'disabled') and self.disabled:
                show_links = False
            else:
                show_links = True
        if style == "inline":
            the_class = 'danavlinks dainline'
            interior_class = 'dainlineinside'
            a_class = "btn " + server.button_class_prefix + "secondary danavlink "
        else:
            if not self.visible():
                return ''
            the_class = 'danavlinks'
            interior_class = None
            a_class = None
        return '  <div class="dasections"><div class="' + the_class + '">' + "\n" + server.navigation_bar(self, this_thread.interview, wrapper=False, inner_div_class=interior_class, a_class=a_class, show_links=show_links, show_nesting=False, include_arrows=True) + '  </div></div>' + "\n"

# word('This field is required.')
# word('Country Code')
# word('First Subdivision')
# word('Second Subdivision')
# word('Third Subdivision')
word_collection = {
    'en': {
        'This field is required.': 'You need to fill this in.',
        "Country Code": 'Country Code (e.g., "us")',
        "First Subdivision": 'State Abbreviation (e.g., "NY")',
        "Second Subdivision": "County",
        "Third Subdivision": "Municipality",
    }
}

ordinal_numbers = {
}

nice_numbers = {
}


class WebFunc:
    pass
server = WebFunc()


def null_func(*pargs, **kwargs):  # pylint: disable=unused-argument
    return None


def null_func_dict(*pargs, **kwargs):  # pylint: disable=unused-argument
    return {}


def null_func_str(*pargs, **kwargs):  # pylint: disable=unused-argument
    return ''


def null_func_obj(*pargs, **kwargs):  # pylint: disable=unused-argument
    return WebFunc()


def null_func_func(*pargs, **kwargs):  # pylint: disable=unused-argument
    return null_func

server.SavedFile = null_func_obj
server.absolute_filename = null_func
server.add_privilege = null_func
server.add_user_privilege = null_func
server.alchemy_url = null_func_str
server.connect_args = null_func_str
server.applock = null_func
server.bg_action = null_func
server.ocr_google_in_background = null_func
server.button_class_prefix = 'btn-'
server.chat_partners_available = null_func
server.chord = null_func_func
server.create_user = null_func
server.invite_user = null_func
server.daconfig = {}
server.debug = False
server.debug_status = False
server.default_country = 'US'
server.default_dialect = 'us'
server.default_voice = None
server.default_language = 'en'
server.default_locale = 'US.utf8'
try:
    server.default_timezone = tzlocal.get_localzone_name()
except:
    server.default_timezone = 'America/New_York'
server.delete_answer_json = null_func
server.delete_record = null_func
server.fg_make_pdf_for_word_path = null_func
server.fg_make_png_for_pdf = null_func
server.fg_make_png_for_pdf_path = null_func
server.file_finder = null_func_dict
server.file_number_finder = null_func_dict
server.file_privilege_access = null_func
server.file_set_attributes = null_func
server.file_user_access = null_func
server.fix_pickle_obj = null_func_dict
server.generate_csrf = null_func
server.get_chat_log = null_func
server.get_ext_and_mimetype = null_func
server.get_new_file_number = null_func
server.get_privileges_list = null_func
server.get_question_data = null_func
server.get_secret = null_func
server.get_session_variables = null_func
server.get_short_code = null_func
server.get_sms_session = null_func_dict
server.get_user_info = null_func
server.get_user_list = null_func
server.get_user_object = null_func_obj
server.go_back_in_session = null_func
server.hostname = 'localhost'
server.initiate_sms_session = null_func
server.interview_menu = null_func
server.main_page_parts = {}
server.make_png_for_pdf = null_func
server.make_user_inactive = null_func
server.navigation_bar = null_func
server.ocr_finalize = null_func
server.ocr_page = null_func
server.path_from_reference = null_func_str
server.read_answer_json = null_func
server.read_records = null_func
server.remove_privilege = null_func
server.remove_user_privilege = null_func
server.retrieve_emails = null_func
server.save_numbered_file = null_func
server.send_fax = null_func
server.send_mail = null_func
server.server_redis = None
server.server_redis_user = None
server.server_sql_defined = null_func
server.server_sql_delete = null_func
server.server_sql_get = null_func
server.server_sql_keys = null_func
server.server_sql_set = null_func
server.create_session = null_func
server.set_session_variables = null_func
server.set_user_info = null_func
server.sms_body = null_func_dict
server.task_ready = null_func
server.terminate_sms_session = null_func
server.twilio_config = {}
server.url_finder = null_func_dict
server.url_for = null_func
server.user_id_dict = null_func
server.user_interviews = null_func
server.variables_snapshot_connection = null_func
server.wait_for_task = null_func
server.worker_convert = null_func
server.write_answer_json = null_func
server.write_record = null_func
server.to_text = null_func_str
server.transform_json_variables = null_func
server.get_login_url = null_func_dict
server.run_action_in_session = null_func_dict
server.invite_user = null_func
server.get_url = null_func_dict


def write_record(key, data):
    """Store data in the SQL database under the given key.

    Args:
        key (str): A string key to associate with the record.
        data: The data to store. Must be pickleable.

    Returns:
        int: The unique integer ID of the saved record.
    """
    return server.write_record(key, data)


def read_records(key):
    """Return all records stored under the given key.

    Args:
        key (str): The string key used when calling ``write_record()``.

    Returns:
        dict: A dictionary mapping unique integer record IDs to the stored data.
    """
    return server.read_records(key)


def delete_record(key, the_id):
    """Delete a record from the SQL database by key and ID.

    Args:
        key (str): The string key associated with the record.
        the_id (int): The unique integer ID of the record to delete.
    """
    return server.delete_record(key, the_id)


def url_of(file_reference, **kwargs):
    """Return a URL to a file within a docassemble package or to a page in the application.

    The ``file_reference`` can be a filename like ``'brochure.pdf'`` (relative
    to the current package's ``static`` folder), a package-qualified reference
    like ``'docassemble.mypackage:data/static/file.pdf'``, a ``DAFile`` object,
    or one of several special strings (``'login'``, ``'register'``, ``'root'``,
    ``'interview'``, ``'temp_url'``, ``'login_url'``, etc.). Keyword arguments
    are passed as URL parameters.

    Args:
        file_reference: A filename, package-qualified reference, DAFile object,
            or special string identifying the target.
        **kwargs: Additional URL parameters or control arguments like
            ``_external=True`` for a full URL or ``_attachment=True`` to
            trigger a download.

    Returns:
        str: A URL string.
    """
    if file_reference == 'temp_url':
        url = kwargs.get('url', None)
        if url is None:
            raise DAError("url_of: a url keyword parameter must accompany temp_url")
        expire = kwargs.get('expire', None)
        local = kwargs.get('local', False)
        one_time = kwargs.get('one_time', False)
        if expire is None:
            expire = 60*60*24*90
        try:
            expire = int(expire)
            assert expire > 0
        except:
            raise DAError("url_of: invalid expire value")
        return temp_redirect(url, expire, bool(local), bool(one_time))
    if file_reference == 'login_url':
        username = kwargs.get('username', None)
        password = kwargs.get('password', None)
        if username is None or password is None:
            raise DAError("url_of: username and password must accompany login_url")
        info = {'username': username, 'password': password}
        for param in ('expire', 'url_args', 'next', 'i', 'session', 'resume_existing'):
            if param in kwargs and kwargs[param] is not None:
                info[param] = kwargs[param]
        result = server.get_login_url(**info)
        if result['status'] == 'success':
            return result['url']
        raise DAError("url_of: " + result['message'])
    if 'package' not in kwargs:
        kwargs['_package'] = get_current_package()
    if 'question' not in kwargs:
        kwargs['_question'] = get_current_question()
    if kwargs.get('attachment', False):
        kwargs['_attachment'] = True
    return server.url_finder(file_reference, **kwargs)


def server_capabilities():
    """Return a dictionary of boolean flags indicating what the server supports.

    Keys include ``'sms'``, ``'fax'``, ``'google_login'``, ``'facebook_login'``,
    ``'auth0_login'``, ``'keycloak_login'``, ``'authentik_login'``,
    ``'azure_login'``, ``'phone_login'``, ``'voicerss'``, ``'s3'``,
    ``'azure'``, ``'github'``, ``'pypi'``, ``'googledrive'``, and
    ``'google_maps'``.

    Returns:
        dict: A dictionary mapping capability names to True/False values.
    """
    result = {'sms': False, 'fax': False, 'google_login': False, 'facebook_login': False, 'auth0_login': False, 'keycloak_login': False, 'authentik_login': False, 'azure_login': False, 'miniorange_login': False, 'phone_login': False, 'voicerss': False, 's3': False, 'azure': False, 'github': False, 'pypi': False, 'googledrive': False, 'google_maps': False}
    if 'twilio' in server.daconfig and isinstance(server.daconfig['twilio'], (list, dict)):
        if isinstance(server.daconfig['twilio'], list):
            tconfigs = server.daconfig['twilio']
        else:
            tconfigs = [server.daconfig['twilio']]
        for tconfig in tconfigs:
            if 'enable' in tconfig and not tconfig['enable']:
                continue
            result['sms'] = True
            if tconfig.get('fax', False):
                result['fax'] = True
            if 'phone login' in server.daconfig:
                result['phone_login'] = True
    if 'oauth' in server.daconfig and isinstance(server.daconfig['oauth'], dict):
        oauth_providers = [
            ('google', 'google_login'),
            ('facebook', 'facebook_login'),
            ('azure', 'azure_login'),
            ('miniorange', 'miniorange_login'),
            ('auth0', 'auth0_login'),
            ('keycloak', 'keycloak_login'),
            ('authentik', 'authentik_login'),
            ('googledrive', 'googledrive'),
            ('github', 'github')
        ]
        for provider, result_key in oauth_providers:
            if provider in server.daconfig['oauth'] and isinstance(server.daconfig['oauth'][provider], dict) and ('enable' not in server.daconfig['oauth'][provider] or server.daconfig['oauth'][provider]['enable']):
                result[result_key] = True
    if 'pypi' in server.daconfig and server.daconfig['pypi'] is True:
        result['pypi'] = True
    if 'google' in server.daconfig and isinstance(server.daconfig['google'], dict) and ('google maps api key' in server.daconfig['google'] or 'api key' in server.daconfig['google']):
        result['google_maps'] = True
    for key in ['voicerss', 's3', 'azure']:
        if key in server.daconfig and isinstance(server.daconfig[key], dict):
            if not ('enable' in server.daconfig[key] and not server.daconfig[key]['enable']):
                result[key] = True
    return result

# def generate_csrf(*pargs, **kwargs):
#     return server.generate_csrf(*pargs, **kwargs)
# def chat_partners(*pargs, **kwargs):
#     return dict(peer=0, help=0)
# def absolute_filename(*pargs, **kwargs):
#     return server.absolute_filename(*pargs, **kwargs)


def update_server(**kwargs):
    for arg, func in kwargs.items():
        # logmessage("Setting " + str(arg))
        if arg == 'bg_action':
            def worker_wrapper(action, ui_notification, the_func=func, **kwargs):
                return worker_caller(the_func, ui_notification, {'action': action, 'arguments': kwargs})
            setattr(server, arg, worker_wrapper)
        else:
            setattr(server, arg, func)

# the_write_record = basic_write_record

# def set_write_record(func):
#     global the_write_record
#     the_write_record = func

# def write_record(key, data):
#     """Stores the data in a SQL database for later retrieval with the
#     key.  Returns the unique ID integers of the saved record.
#     """
#     return the_write_record(key, data)

# def basic_read_records(key):
#     return {}

# the_read_records = basic_read_records

# def set_read_records(func):
#     global the_read_records
#     the_read_records = func

# def read_records(key):
#     """Returns a dictionary of records that have been stored with
#     write_record() using the given key.  In the dictionary, the key is
#     the unique ID integer of the record and the value is the data that
#     had been stored.
#     """
#     return the_read_records(key)

# def basic_delete_record(key, the_id):
#     return

# the_delete_record = basic_delete_record

# def set_delete_record(func):
#     global the_delete_record
#     the_delete_record = func

# def delete_record(key, the_id):
#     """Deletes a record with the given key and id."""
#     return the_delete_record(key, the_id)

# def set_url_finder(func):
#     global the_url_func
#     the_url_func = func
#     if the_url_func.__doc__ is None:
#         the_url_func.__doc__ = """Returns a URL to a file within a docassemble package."""

# def basic_generate_csrf(*pargs, **kwargs):
#     return None

# the_generate_csrf = basic_generate_csrf

# def generate_csrf(*pargs, **kwargs):
#     return the_generate_csrf(*pargs, **kwargs)

# def set_generate_csrf(func):
#     global the_generate_csrf
#     the_generate_csrf = func

# def null_worker(*pargs, **kwargs):
#     # logmessage("Got to null worker")
#     return None

# bg_action = null_worker

# worker_convert = null_worker


class GenericObject:

    def __init__(self):
        self.user = None
        self.role = 'user'

# class ThreadVariables(threading.local):
#     language = server.default_language
#     dialect = server.default_dialect
#     country = server.default_country
#     locale = server.default_locale
#     current_info = {}
#     internal = {}
#     # user_dict = None
#     initialized = False
#     # redis = None
#     session_id = None
#     current_package = None
#     interview = None
#     interview_status = None
#     evaluation_context = None
#     docx_template = None
#     gathering_mode = {}
#     global_vars = GenericObject()
#     current_variable = []
#     # template_vars = []
#     open_files = set()
#     # markdown = markdown.Markdown(extensions=[smartyext, 'markdown.extensions.sane_lists', 'markdown.extensions.tables', 'markdown.extensions.attr_list'], output_format='html5')
#     markdown = markdown.Markdown(extensions=[smartyext, 'markdown.extensions.sane_lists', 'markdown.extensions.tables', 'markdown.extensions.attr_list'], output_format='html5')
#     # temporary_resources = set()
#     saved_files = {}
#     message_log = []
#     misc = {}
#     prevent_going_back = False
#     current_question = None
#     def __init__(self, **kw):
#         if self.initialized:
#             raise SystemError('__init__ called too many times')
#         self.initialized = True
#         self.__dict__.update(kw)

this_thread = threading.local()

def populate_this_thread_defaults():
    this_thread.language = server.default_language
    this_thread.dialect = server.default_dialect
    this_thread.voice = server.default_voice
    this_thread.country = server.default_country
    this_thread.locale = server.default_locale
    this_thread.current_info = {}
    this_thread.internal = {}
    this_thread.initialized = False
    this_thread.session_id = None
    this_thread.current_package = None
    this_thread.interview = None
    this_thread.interview_status = None
    this_thread.evaluation_context = None
    this_thread.gathering_mode = {}
    this_thread.global_vars = GenericObject()
    this_thread.current_variable = []
    this_thread.open_files = set()
    this_thread.markdown = markdown.Markdown(extensions=['smarty', 'markdown.extensions.sane_lists', 'markdown.extensions.tables', 'markdown.extensions.attr_list', 'markdown.extensions.md_in_html', 'footnotes'], output_format='html5')
    this_thread.saved_files = {}
    this_thread.message_log = []
    this_thread.misc = {}
    this_thread.probing = False
    this_thread.prevent_going_back = False
    this_thread.current_question = None
    this_thread.current_section = None

populate_this_thread_defaults()


def enable_threading():
    global this_thread
    this_thread = SimpleNamespace()
    populate_this_thread_defaults()


def backup_thread_variables():
    reset_context()
    for key in ('pending_error', 'docx_subdocs', 'dbcache'):
        if key in this_thread.misc:
            del this_thread.misc[key]
    backup = {}
    for key in ('interview', 'interview_status', 'open_files', 'current_question'):
        if hasattr(this_thread, key):
            backup[key] = getattr(this_thread, key)
    for key in ['language', 'dialect', 'country', 'locale', 'current_info', 'internal', 'initialized', 'session_id', 'current_package', 'interview', 'interview_status', 'evaluation_context', 'gathering_mode', 'global_vars', 'current_variable', 'saved_files', 'message_log', 'misc', 'probing', 'prevent_going_back', 'current_question']:
        if hasattr(this_thread, key):
            backup[key] = getattr(this_thread, key)
            if key == 'global_vars':
                this_thread.global_vars = GenericObject()
            elif key == 'misc':
                for key in [item for item in this_thread.misc.keys() if item.startswith('yaml_')]:
                    del this_thread.misc[key]
                setattr(this_thread, key, copy.deepcopy(this_thread.misc))
            elif key == 'current_info':
                setattr(this_thread, key, copy.deepcopy(getattr(this_thread, key)))
            elif key in ('internal', 'gathering_mode', 'saved_files'):
                setattr(this_thread, key, {})
            elif key in ('current_variable', 'message_log'):
                setattr(this_thread, key, [])
    return backup


def restore_thread_variables(backup):
    # logmessage("restore_thread_variables")
    for key in list(backup.keys()):
        setattr(this_thread, key, backup[key])


def background_response(*pargs, **kwargs):
    """Finish a background task and optionally return a result.

    Must be called at the end of every background action code block.
    When called with a value, that value is retrievable via ``.get()``
    on the task object.  Can also be called with keyword arguments to
    populate target areas on the screen, set field values, run
    JavaScript, or trigger a screen refresh.

    Args:
        *pargs: An optional return value, or special control strings
            such as ``'refresh'``, ``'javascript'``, ``'flash'``, or
            ``'fields'``.
        **kwargs: Optional keyword arguments such as ``target`` and
            ``content`` for populating ``[TARGET ...]`` areas.
    """
    raise BackgroundResponseError(*pargs, **kwargs)


def background_response_action(*pargs, **kwargs):
    """Finish a background task by triggering an action to save values to the interview dictionary.

    Use this instead of :func:`background_response` when the background task
    needs to persist changes to interview variables.  The first argument is
    the name of the action to run; keyword arguments are passed to that action.

    Args:
        *pargs: The action name as the first positional argument.
        **kwargs: Arguments to pass to the specified action.
    """
    raise BackgroundResponseActionError(*pargs, **kwargs)


def background_error_action(*pargs, **kwargs):
    """Register an action to run if the current background task raises an error.

    Sets up an error handler for the background task.  If the task raises an
    exception, the specified action will be run.

    Args:
        *pargs: The action name as the first positional argument.
        **kwargs: Arguments to pass to the error-handling action.
    """
    this_thread.current_info['on_error'] = {'action': pargs[0], 'arguments': kwargs}


def background_action(*pargs, **kwargs):
    """Start an interview action as a background (Celery) task and return immediately.

    The specified action runs asynchronously in a Celery worker.  Returns a
    task object whose ``.ready()``, ``.failed()``, ``.wait()``, ``.get()``,
    and ``.result()`` methods can be used to monitor and retrieve the result.

    Args:
        *pargs: The action name as the first positional argument, and an
            optional second argument for the UI notification mode.
        **kwargs: Arguments to pass to the action, accessible inside the
            action via :func:`action_argument`.

    Returns:
        A task object representing the background task.
    """
    action = pargs[0]
    if len(pargs) > 1:
        ui_notification = pargs[1]
    else:
        ui_notification = None
    return server.bg_action(action, ui_notification, **kwargs)


class BackgroundResult:

    def __init__(self, result):
        for attr in ('value', 'error_type', 'error_trace', 'error_message', 'variables'):
            if hasattr(result, attr):
                setattr(self, attr, getattr(result, attr))
            else:
                setattr(self, attr, None)


class MyAsyncResult:

    def wait(self):
        if not hasattr(self, '_cached_result'):
            self._cached_result = BackgroundResult(server.worker_convert(self.obj).get())
        return True

    def failed(self):
        if not hasattr(self, '_cached_result'):
            self._cached_result = BackgroundResult(server.worker_convert(self.obj).get())
        if self._cached_result.error_type is not None:
            return True
        return False

    def ready(self):
        return server.worker_convert(self.obj).ready()

    def result(self):
        if not hasattr(self, '_cached_result'):
            self._cached_result = BackgroundResult(server.worker_convert(self.obj).get())
        return self._cached_result

    def get(self):
        if not hasattr(self, '_cached_result'):
            self._cached_result = BackgroundResult(server.worker_convert(self.obj).get())
        return self._cached_result.value

    def revoke(self, terminate=True):
        return server.worker_convert(self.obj).revoke(terminate=terminate)

    def status(self):
        return server.worker_convert(self.obj).status

    def state(self):
        return server.worker_convert(self.obj).state

    def date_done(self):
        return server.worker_convert(self.obj).date_done


def worker_caller(func, ui_notification, action):
    # logmessage("Got to worker_caller in functions")
    result = MyAsyncResult()
    result.obj = func.delay(this_thread.current_info['yaml_filename'], this_thread.current_info['user'], this_thread.current_info['session'], this_thread.current_info['secret'], this_thread.current_info['url'], this_thread.current_info['url_root'], action, extra=ui_notification)
    if ui_notification is not None:
        worker_key = 'da:worker:uid:' + str(this_thread.current_info['session']) + ':i:' + str(this_thread.current_info['yaml_filename']) + ':userid:' + str(this_thread.current_info['user']['the_user_id'])
        # logmessage("worker_caller: id is " + str(result.obj.id) + " and key is " + worker_key)
        server.server_redis.rpush(worker_key, result.obj.id)
    # logmessage("worker_caller: id is " + str(result.obj.id))
    return result

# def null_chat_partners(*pargs, **kwargs):
#     return dict(peer=0, help=0)

# chat_partners_available_func = null_chat_partners

# def set_chat_partners_available(func):
#     global chat_partners_available_func
#     chat_partners_available_func = func

# def set_worker(func, func_two):
#     def new_func(action, ui_notification, **kwargs):
#         return worker_caller(func, ui_notification, {'action': action, 'arguments': kwargs})
#     global bg_action
#     bg_action = new_func
#     global worker_convert
#     worker_convert = func_two
#     return

# server_redis = None

# def set_server_redis(target):
#     global server_redis
#     server_redis = target


class SafeYaml:
    def __init__(self, yaml_type):
        self._yaml_type = yaml_type

    def _get_yaml(self):
        if self._yaml_type not in this_thread.misc:
            if self._yaml_type == 'yaml_bytesyaml':
                the_yaml = ruamel.yaml.YAML(typ=['safe', 'bytes'])
            else:
                the_yaml = ruamel.yaml.YAML(typ=['safe', 'string'])
            if self._yaml_type == 'yaml_prettyyaml':
                the_yaml.indent(mapping=2, sequence=4, offset=2)
                the_yaml.default_flow_style = False
                the_yaml.default_style = '|'
                the_yaml.allow_unicode = True
            elif self._yaml_type == 'yaml_altyaml':
                the_yaml.indent(mapping=2, sequence=4, offset=2)
                the_yaml.default_flow_style = False
                the_yaml.default_style = '|'
                the_yaml.allow_unicode = True
            elif self._yaml_type == 'yaml_bytesyaml':
                the_yaml.default_flow_style = False
                the_yaml.default_style = '"'
                the_yaml.allow_unicode = True
                the_yaml.width = 10000
            elif self._yaml_type == 'yaml_altyamlstring':
                the_yaml.default_flow_style = False
                the_yaml.default_style = '"'
                the_yaml.allow_unicode = True
                the_yaml.width = 10000
            this_thread.misc[self._yaml_type] = the_yaml
        return this_thread.misc[self._yaml_type]

    def load(self, *pargs, **kwargs):
        return self._get_yaml().load(*pargs, **kwargs)

    def load_all(self, *pargs, **kwargs):
        return self._get_yaml().load_all(*pargs, **kwargs)

    def dump_to_string(self, *pargs, **kwargs):
        return self._get_yaml().dump_to_string(*pargs, **kwargs)

    def dump_to_bytes(self, *pargs, **kwargs):
        return self._get_yaml().dump_to_bytes(*pargs, **kwargs)

safeyaml = SafeYaml('yaml_safeyaml')
altyaml = SafeYaml('yaml_altyaml')
prettyyaml = SafeYaml('yaml_prettyyaml')
bytesyaml = SafeYaml('yaml_bytesyaml')
altyamlstring = SafeYaml('yaml_altyamlstring')


def ordinal_function_en(i, **kwargs):
    try:
        i = int(i)
    except:
        i = 0
    use_word = kwargs.get('use_word', None)
    if use_word is True:
        kwargs['function'] = 'ordinal'
    elif use_word is False:
        kwargs['function'] = 'ordinal_num'
    else:
        if i < 11:
            kwargs['function'] = 'ordinal'
        else:
            kwargs['function'] = 'ordinal_num'
    return number_to_word(i, **kwargs)

ordinal_functions = {
    'en': ordinal_function_en,
    '*': ordinal_function_en
}


def fix_punctuation(text, mark=None, other_marks=None):
    """Ensure the text ends with a punctuation mark, adding one if necessary.

    Args:
        text (str): The text to check.
        mark (str, optional): The punctuation mark to append if none is
            present. Defaults to ``'.'``.
        other_marks (list, optional): A list of punctuation marks that are
            considered acceptable endings. Defaults to ``['.', '?', '!']``.

    Returns:
        str: The text, possibly with a punctuation mark appended.
    """
    ensure_definition(text, mark, other_marks)
    if other_marks is None:
        other_marks = ['.', '?', '!']
    if not isinstance(other_marks, list):
        other_marks = list(other_marks)
    if mark is None:
        mark = '.'
    text = text.rstrip()
    if mark == '':
        return text
    for end_mark in set([mark] + other_marks):
        if text.endswith(end_mark):
            return text
    return text + mark


def item_label(num, level=None, punctuation=True):
    """Return a formatted list item label for a given zero-based index and outline level.

    Args:
        num (int): The zero-based index of the item.
        level (int, optional): The outline level (0–6).  Level 0 uses
            Roman numerals, 1 uses uppercase letters, 2 and 4 use Arabic
            numerals, 3 and 5 use lowercase letters, 6 uses lowercase Roman
            numerals. Defaults to ``0``.
        punctuation (bool, optional): If ``True``, appends the appropriate
            punctuation mark. Defaults to ``True``.

    Returns:
        str: The formatted label (e.g. ``'I.'``, ``'A.'``, ``'1.'``,
            ``'a)'``, ``'(1)'``, ``'(a)'``, ``'i)'``).
    """
    ensure_definition(num, level, punctuation)
    if level is None:
        level = 0
    level = int(float(level)) % 7
    if level == 0:
        string = roman(num)
    elif level == 1:
        string = alpha(num)
    elif level == 2:
        string = str(num + 1)
    elif level == 3:
        string = alpha(num, case='lower')
    elif level == 4:
        string = str(num + 1)
    elif level == 5:
        string = alpha(num, case='lower')
    elif level == 6:
        string = roman(num, case='lower')
    else:
        string = str(num + 1)
    if not punctuation:
        return string
    if level < 3:
        return string + '.'
    if level in (3, 6):
        return string + ')'
    return '(' + string + ')'


def alpha(num, case=None):
    """Return a letter label for a zero-based index (A, B, … Z, AA, AB, …).

    Args:
        num (int): The zero-based index.
        case (str, optional): ``'upper'`` for uppercase (default) or
            ``'lower'`` for lowercase.

    Returns:
        str: The alphabetical label (e.g. ``alpha(0)`` returns ``'A'``,
            ``alpha(25)`` returns ``'Z'``, ``alpha(26)`` returns ``'AA'``).
    """
    ensure_definition(num, case)
    if case is None:
        case = 'upper'
    div = num + 1
    string = ""
    while div > 0:
        modulus = (div - 1) % 26
        string = chr(65 + modulus) + string
        div = int((div - modulus)/26)
    if case == 'lower':
        return string.lower()
    return string


def roman(num, case=None):
    """Return a Roman numeral for a zero-based index.

    Args:
        num (int): The zero-based index (0–3998).
        case (str, optional): ``'upper'`` for uppercase (default) or
            ``'lower'`` for lowercase.

    Returns:
        str: The Roman numeral for ``num + 1`` (e.g. ``roman(0)`` returns
            ``'I'``, ``roman(65)`` returns ``'LXVI'``).

    Raises:
        ValueError: If ``num + 1`` is not between 1 and 3999.
        TypeError: If ``num`` is not an integer.
    """
    ensure_definition(num, case)
    if case is None:
        case = 'upper'
    num = num + 1
    if not isinstance(num, int):
        raise TypeError("expected integer, got %s" % type(num))
    if not 0 < num < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500,  400, 100,  90, 50,  40, 10,  9,   5,   4,  1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = ""
    for indexno, the_int in enumerate(ints):
        count = int(num / the_int)
        result += nums[indexno] * count
        num -= the_int * count
    if case == 'lower':
        return result.lower()
    return result


def words():
    return word_collection[this_thread.language]


class LazyWord:

    def __init__(self, *args, **kwargs):
        if len(kwargs) > 0:
            self.original = args[0] % kwargs
        else:
            self.original = args[0]

    def __mod__(self, other):
        return word(self.original) % other

    def __str__(self):
        return word(self.original)


class LazyArray:

    def __init__(self, array):
        self.original = array

    def compute(self):
        return [word(item) for item in self.original]

    def copy(self):
        return self.compute().copy()

    def pop(self, *pargs):
        return str(self.original.pop(*pargs))

    def __add__(self, other):
        return self.compute() + other

    def index(self, *pargs, **kwargs):
        return self.compute().index(*pargs, **kwargs)

    def clear(self):
        self.original = []

    def append(self, other):
        self.original.append(other)

    def remove(self, other):
        self.original.remove(other)

    def extend(self, other):
        self.original.extend(other)

    def __contains__(self, item):
        return self.compute().__contains__(item)

    def __iter__(self):
        return self.compute().__iter__()

    def __len__(self):
        return self.compute().__len__()

    def __delitem__(self, index):
        self.original.__delitem__(index)

    def __reversed__(self):
        return self.compute().__reversed__()

    def __setitem__(self, index, the_value):
        return self.original.__setitem__(index, the_value)

    def __getitem__(self, index):
        return self.compute()[index]

    def __str__(self):
        return str(self.compute())

    def __repr__(self):
        return repr(self.compute())

    def __eq__(self, other):
        return self.original == other


def word(the_word, **kwargs):
    """Return the word translated into the current language.

    If no translation is found for the current language, the input is
    returned unchanged.  Used throughout docassemble to support
    multilingual interviews.

    Args:
        the_word (str): The word or phrase to translate.
        **kwargs: Optional keyword arguments.  Pass ``language`` to
            look up a translation for a specific language, or
            ``capitalize=True`` to capitalize the result.

    Returns:
        str: The translated (or original) word.
    """
    # Currently, no kwargs are used, but in the future, this function could be
    # expanded to use kwargs.  For example, for languages with gendered words,
    # the gender could be passed as a keyword argument.
    if the_word is True:
        the_word = 'yes'
    elif the_word is False:
        the_word = 'no'
    elif the_word is None:
        the_word = "I don't know"
    if isinstance(the_word, LazyWord):
        the_word = the_word.original
    try:
        the_word = word_collection[kwargs.get('language', this_thread.language)][the_word]
    except:
        the_word = str(the_word)
    if kwargs.get('capitalize', False):
        return capitalize(the_word)
    return the_word


def update_language_function(lang, term, func):
    if term not in language_functions:
        language_functions[term] = {}
    language_functions[term][lang] = func


def update_nice_numbers(lang, defs):
    if lang not in nice_numbers:
        nice_numbers[lang] = {}
    for number, the_word in defs.items():
        nice_numbers[lang][str(number)] = the_word


def update_ordinal_numbers(lang, defs):
    if lang not in ordinal_numbers:
        ordinal_numbers[lang] = {}
    for number, the_word in defs.items():
        ordinal_numbers[lang][str(number)] = the_word


def update_ordinal_function(lang, func):
    ordinal_functions[lang] = func


def update_word_collection(lang, defs):
    if lang not in word_collection:
        word_collection[lang] = {}
    for the_word, translation in defs.items():
        if translation is not None:
            word_collection[lang][the_word] = translation

# def set_da_config(config):
#     global daconfig
#     daconfig = config


def get_config(key, none_value=None):
    """Return a value from the docassemble configuration file.

    Args:
        key (str): The configuration directive to look up.
        none_value (optional): The value to return if the key is not found in
            the configuration. Defaults to None.

    Returns:
        The configuration value associated with the key, or ``none_value``
            if the key is not present.
    """
    return server.daconfig.get(key, none_value)

# def set_default_language(lang):
#     global default_language
#     default_language = lang

# def set_default_dialect(dialect):
#     global default_dialect
#     default_dialect = dialect
#     return

# def set_default_country(country):
#     global default_country
#     default_country = country
#     return

# def set_default_timezone(timezone):
#     global default_timezone
#     default_timezone = timezone
#     return


def get_default_timezone():
    """Return the default timezone string for the server.

    Returns the server's local timezone unless a default timezone is configured
    in the docassemble configuration.

    Returns:
        str: A timezone string such as ``'America/New_York'``.
    """
    return server.default_timezone

# def reset_thread_local():
#     this_thread.open_files = set()
#     this_thread.temporary_resources = set()

# def reset_thread_variables():
#     this_thread.saved_files = {}
#     this_thread.message_log = []


def reset_local_variables():
    # logmessage("reset_local_variables")
    this_thread.language = server.default_language
    this_thread.dialect = server.default_dialect
    this_thread.voice = server.default_voice
    this_thread.country = server.default_country
    this_thread.locale = server.default_locale
    this_thread.session_id = None
    this_thread.interview = None
    this_thread.interview_status = None
    this_thread.evaluation_context = None
    this_thread.gathering_mode = {}
    this_thread.global_vars = GenericObject()
    this_thread.current_variable = []
    # this_thread.template_vars = []
    this_thread.open_files = set()
    this_thread.saved_files = {}
    this_thread.message_log = []
    this_thread.misc = {}
    this_thread.probing = False
    this_thread.current_info = {}
    this_thread.current_package = None
    this_thread.current_question = None
    this_thread.current_section = None
    this_thread.internal = {}
    this_thread.markdown = markdown.Markdown(extensions=['smarty', 'markdown.extensions.sane_lists', 'markdown.extensions.tables', 'markdown.extensions.attr_list', 'markdown.extensions.md_in_html', 'footnotes'], output_format='html5')
    this_thread.prevent_going_back = False


def prevent_going_back():
    """Disable the back button so the user cannot revisit previous questions.

    Once called, the user will not be able to go back and change any answers
    entered before this point in the interview.
    """
    this_thread.prevent_going_back = True


def set_language(lang, dialect=None, voice=None):
    """Set the language used for linguistic functions and the web application.

    Does not change the Python locale; call ``update_locale()`` for that.
    Should be called in an ``initial`` code block so it takes effect on every
    page load.

    Args:
        lang (str): A lowercase ISO-639-1 or ISO-639-3 language code
            (e.g., ``'en'``, ``'es'``, ``'fr'``).
        dialect (str, optional): A dialect code for the text-to-speech engine.
            Defaults to None.
        voice (str, optional): A voice name for the text-to-speech engine.
            Defaults to None.
    """
    try:
        if dialect:
            this_thread.dialect = dialect
        elif lang != this_thread.language:
            this_thread.dialect = None
    except:
        pass
    try:
        if voice:
            this_thread.voice = voice
        elif lang != this_thread.language:
            this_thread.voice = None
    except:
        pass
    this_thread.language = lang


def get_language():
    """Return the current language code.

    Returns:
        str: The current language code (e.g., ``'en'``, ``'es'``).
    """
    return this_thread.language


def set_country(country):
    """Set the current country used for phone number formatting and other locale features.

    Args:
        country (str): A two-letter uppercase ISO 3166-1 alpha-2 country code
            (e.g., ``'US'``, ``'GB'``, ``'DE'``).
    """
    this_thread.country = country


def get_country():
    """Return the current country code.

    Returns:
        str: A two-letter uppercase ISO 3166-1 alpha-2 country code
            (e.g., ``'US'``). Defaults to ``'US'`` unless configured otherwise.
    """
    return this_thread.country


def get_dialect():
    """Return the current dialect.

    Returns:
        str: The dialect code set by the ``dialect`` keyword argument to
            :func:`set_language`, or ``None`` if no dialect has been set.
    """
    return this_thread.dialect


def get_voice():
    """Return the current voice.

    Returns:
        str: The voice name set by the ``voice`` keyword argument to
            :func:`set_language`, or ``None`` if no voice has been set.
    """
    return this_thread.voice


def set_locale(*pargs, **kwargs):
    """Set the current locale string and/or locale convention overrides.

    Calling ``set_locale('FR.utf8')`` stores the locale string so that
    :func:`get_locale` returns it.  The actual Python locale does not change
    until :func:`update_locale` is called.  Keyword arguments such as
    ``currency_symbol`` override individual locale conventions used by
    functions like :func:`currency` and :func:`currency_symbol`.

    Args:
        *pargs: An optional locale string (e.g. ``'FR.utf8'``).
        **kwargs: Locale convention overrides (e.g. ``currency_symbol='€'``).
    """
    if len(pargs) == 1:
        this_thread.locale = pargs[0]
    if len(kwargs):
        this_thread.misc['locale_overrides'] = kwargs


def get_locale(*pargs):
    """Return the current locale setting or a specific locale convention.

    With no arguments, returns the locale string previously set with
    :func:`set_locale`.  With one argument, returns the value of the named
    locale convention (e.g. ``'currency_symbol'``), taking into account any
    overrides set with :func:`set_locale`.

    Args:
        *pargs: An optional locale convention name (e.g.
            ``'currency_symbol'``).

    Returns:
        str or None: The locale string when called with no arguments, or the
            value of the requested locale convention (``None`` if not found).
    """
    if len(pargs) == 1:
        if 'locale_overrides' in this_thread.misc and pargs[0] in this_thread.misc['locale_overrides']:
            return this_thread.misc['locale_overrides'][pargs[0]]
        return locale.localeconv().get(pargs[0], None)
    return this_thread.locale


def get_currency_symbol():
    """Returns the current setting for the currency symbol if there is
    one, and otherwise returns the default currency symbol.

    """
    if 'locale_overrides' in this_thread.misc and 'currency_symbol' in this_thread.misc['locale_overrides']:
        return this_thread.misc['locale_overrides']['currency_symbol']
    return currency_symbol()


def update_locale():
    """Update the Python locale based on the current language and locale settings.

    Applies the locale string previously set with :func:`set_locale` (combined
    with the current language from :func:`get_language` when necessary) so that
    Python's ``locale`` module reflects the desired locale.  This is required
    for functions like :func:`currency` and :func:`currency_symbol` to produce
    locale-appropriate formatting.
    """
    if '_' in this_thread.locale:
        the_locale = str(this_thread.locale)
    else:
        the_locale = str(this_thread.language) + '_' + str(this_thread.locale)
    try:
        locale.setlocale(locale.LC_ALL, the_locale)
    except BaseException as err:
        logmessage("update_locale error: unable to set the locale to " + the_locale)
        logmessage(err.__class__.__name__ + ": " + str(err))
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')


def comma_list_en(*pargs, **kwargs):
    """Returns the arguments separated by commas.  If the first argument is a list,
    that list is used.  Otherwise, the arguments are treated as individual items.
    See also comma_and_list()."""
    ensure_definition(*pargs, **kwargs)
    comma_string = kwargs.get('comma_string', ', ')
    the_list = []
    for parg in pargs:
        if isinstance(parg, str):
            the_list.append(parg)
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')) or isinstance(parg, Iterable):
            for sub_parg in parg:
                the_list.append(str(sub_parg))
        else:
            the_list.append(str(parg))
    return comma_string.join(the_list)


def comma_and_list_es(*pargs, **kwargs):
    if 'and_string' not in kwargs:
        kwargs['and_string'] = 'y'
    return comma_and_list_en(*pargs, **kwargs)


def comma_and_list_de(*pargs, **kwargs):
    if 'and_string' not in kwargs:
        kwargs['and_string'] = 'und'
    if 'oxford' not in kwargs:
        kwargs['oxford'] = False
    return comma_and_list_en(*pargs, **kwargs)


def comma_and_list_en(*pargs, **kwargs):
    """Returns an English-language listing of the arguments.  If the first argument is a list,
    that list is used.  Otherwise, the arguments are treated as individual items in the list.
    Use the optional argument oxford=False if you do not want a comma before the "and."
    See also comma_list()."""
    ensure_definition(*pargs, **kwargs)
    and_string = kwargs.get('and_string', word('and'))
    comma_string = kwargs.get('comma_string', ', ')
    if 'oxford' in kwargs and kwargs['oxford'] is False:
        extracomma = ""
    else:
        extracomma = comma_string.strip()
    before_and = kwargs.get('before_and', ' ')
    after_and = kwargs.get('after_and', ' ')
    the_list = []
    for parg in pargs:
        if isinstance(parg, str):
            the_list.append(parg)
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')) or isinstance(parg, Iterable):
            for sub_parg in parg:
                the_list.append(str(sub_parg))
        else:
            the_list.append(str(parg))
    if len(the_list) == 0:
        return str('')
    if len(the_list) == 1:
        return the_list[0]
    if len(the_list) == 2:
        return the_list[0] + before_and + and_string + after_and + the_list[1]
    return comma_string.join(the_list[:-1]) + extracomma + before_and + and_string + after_and + the_list[-1]


def manual_line_breaks(text):
    """Replaces newlines with manual line breaks."""
    if this_thread.evaluation_context == 'docx':
        return re.sub(r' *\r?\n *', '</w:t><w:br/><w:t xml:space="preserve">', str(text))
    return re.sub(r' *\r?\n *', ' [BR] ', str(text))


def add_separators_en(*pargs, **kwargs):
    """Accepts a list and returns a list, with semicolons after each item,
    except "and" after the penultimate item and a period after the
    last.

    """
    ensure_definition(*pargs, **kwargs)
    separator = kwargs.get('separator', ';')
    last_separator = kwargs.get('last_separator', '; ' + word("and"))
    end_mark = kwargs.get('end_mark', '.')
    the_list = []
    for parg in pargs:
        if isinstance(parg, str):
            the_list.append(parg.rstrip())
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')) or isinstance(parg, Iterable):
            for sub_parg in parg:
                the_list.append(str(sub_parg).rstrip())
        else:
            the_list.append(str(parg).rstrip())
    if len(the_list) == 0:
        return the_list
    if len(the_list) == 1:
        return [fix_punctuation(the_list[0], mark=end_mark)]
    for indexno in range(len(the_list) - 2):  # for 4: 0, 1; for 3: 0; for 2: []
        the_list[indexno] = the_list[indexno].rstrip(',')
        the_list[indexno] = fix_punctuation(the_list[indexno], mark=separator)
    if not the_list[-2].endswith(last_separator):
        the_list[-2] = the_list[-2].rstrip(last_separator[0])
        the_list[-2] += last_separator
    the_list[-1] = fix_punctuation(the_list[-1], mark=end_mark)
    return the_list


def need(*pargs):
    """Ensure that the given variables are defined, asking questions if necessary.

    Evaluating each argument causes docassemble to seek its definition
    through the normal interview logic.  The function always returns
    ``True``.  Using ``need()`` is purely for readability; writing
    ``need(x, y)`` is equivalent to writing ``x; y`` in a code block.

    Args:
        *pargs: Variables whose definitions should be ensured.

    Returns:
        bool: Always ``True``.
    """
    ensure_definition(*pargs)
    for argument in pargs:
        argument  # pylint: disable=pointless-statement
    return True


def pickleable_objects(input_dict):
    output_dict = {}
    for key in input_dict:
        if isinstance(input_dict[key], (types.ModuleType, types.FunctionType, TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, FileType)):
            continue
        if key == "__builtins__":
            continue
        output_dict[key] = input_dict[key]
    return output_dict


def ordinal_number_default(the_number, **kwargs):
    """Returns the "first," "second," "third," etc. for a given number.
    ordinal_number(1) returns "first."  For a function that can be used
    on index numbers that start with zero, see ordinal()."""
    num = str(the_number)
    if kwargs.get('use_word', True):
        if this_thread.language in ordinal_numbers and num in ordinal_numbers[this_thread.language]:
            return ordinal_numbers[this_thread.language][num]
        if '*' in ordinal_numbers and num in ordinal_numbers['*']:
            return ordinal_numbers['*'][num]
    if this_thread.language in ordinal_functions:
        language_to_use = this_thread.language
    elif '*' in ordinal_functions:
        language_to_use = '*'
    else:
        language_to_use = 'en'
    return ordinal_functions[language_to_use](the_number, **kwargs)


def salutation_default(indiv, **kwargs):
    """Returns Mr., Ms., etc. for an individual."""
    with_name = kwargs.get('with_name', False)
    with_name_and_punctuation = kwargs.get('with_name_and_punctuation', False)
    ensure_definition(indiv, with_name, with_name_and_punctuation)
    used_gender = False
    if hasattr(indiv, 'salutation_to_use') and indiv.salutation_to_use is not None:
        salut = indiv.salutation_to_use
    elif hasattr(indiv, 'is_doctor') and indiv.is_doctor:
        salut = 'Dr.'
    elif hasattr(indiv, 'is_judge') and indiv.is_judge:
        salut = 'Judge'
    elif hasattr(indiv, 'name') and hasattr(indiv.name, 'suffix') and indiv.name.suffix in ('MD', 'PhD'):
        salut = 'Dr.'
    elif hasattr(indiv, 'name') and hasattr(indiv.name, 'suffix') and indiv.name.suffix == 'J':
        salut = 'Judge'
    elif indiv.gender == 'female':
        used_gender = True
        salut = 'Ms.'
    else:
        used_gender = True
        salut = 'Mr.'
    if with_name_and_punctuation or with_name:
        if used_gender and indiv.gender not in ('male', 'female'):
            salut_and_name = indiv.name.full()
        else:
            salut_and_name = salut + ' ' + indiv.name.last
        if with_name_and_punctuation:
            if hasattr(indiv, 'is_friendly') and indiv.is_friendly:
                punct = ','
            else:
                punct = ':'
            return salut_and_name + punct
        if with_name:
            return salut_and_name
    return salut


def string_to_number(number):
    try:
        float_number = float(number)
        int_number = int(number)
        if float_number == int_number:
            return int_number
        return float_number
    except:
        return number


def number_to_word(number, **kwargs):
    language = kwargs.get('language', None)
    capitalize_arg = kwargs.get('capitalize', False)
    function = kwargs.get('function', None)
    raise_on_error = kwargs.get('raise_on_error', False)
    if function not in ('ordinal', 'ordinal_num'):
        function = 'cardinal'
    if language is None:
        language = get_language()
    for lang, loc in (('en', 'en_GB'), ('en', 'en_IN'), ('es', 'es_CO'), ('es', 'es_VE'), ('fr', 'fr_CH'), ('fr', 'fr_BE'), ('fr', 'fr_DZ'), ('pt', 'pt_BR')):
        if language == lang and this_thread.locale.startswith(loc):
            language = loc
            break
    number = string_to_number(number)
    if raise_on_error:
        the_word = num2words.num2words(number, lang=language, to=function)
    else:
        try:
            the_word = num2words.num2words(number, lang=language, to=function)
        except NotImplementedError:
            the_word = str(number)
    if capitalize_arg:
        return capitalize_function(the_word)
    return the_word


def ordinal_default(the_number, **kwargs):
    """Returns the "first," "second," "third," etc. for a given number, which is expected to
    be an index starting with zero.  ordinal(0) returns "first."  For a more literal ordinal
    number function, see ordinal_number()."""
    result = ordinal_number(int(float(the_number)) + 1, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(result)
    return result


def nice_number_default(the_number, **kwargs):
    """Returns the number as a word in the current language."""
    capitalize_arg = kwargs.get('capitalize', False)
    language = kwargs.get('language', None)
    use_word = kwargs.get('use_word', None)
    ensure_definition(the_number, capitalize_arg, language)
    if language is None:
        language = this_thread.language
    if language in nice_numbers:
        language_to_use = language
    elif '*' in nice_numbers:
        language_to_use = '*'
    else:
        language_to_use = 'en'
    if isinstance(the_number, float):
        the_number = float(decimal.Context(prec=8).create_decimal_from_float(the_number))
    if int(float(the_number)) == float(the_number):
        the_number = int(float(the_number))
        is_integer = True
    else:
        is_integer = False
    if language_to_use in nice_numbers and str(the_number) in nice_numbers[language_to_use]:
        the_word = nice_numbers[language_to_use][str(the_number)]
        if capitalize_arg:
            return capitalize_function(the_word)
        return the_word
    if use_word or (is_integer and 0 <= the_number < 11 and use_word is not False):
        try:
            return number_to_word(the_number, **kwargs)
        except:
            pass
    if isinstance(the_number, int):
        return str(locale.format_string("%d", the_number, grouping=True))
    return str(locale.format_string("%.2f", float(the_number), grouping=True)).rstrip('0')


def quantity_noun_default(the_number, noun, **kwargs):
    as_integer = kwargs.get('as_integer', True)
    capitalize_arg = kwargs.get('capitalize', False)
    language = kwargs.get('language', None)
    ensure_definition(the_number, noun, as_integer, capitalize_arg, language)
    if as_integer:
        the_number = int(round(the_number))
    result = nice_number(the_number, language=language) + " " + noun_plural(noun, the_number, language=language)
    if capitalize_arg:
        return capitalize_function(result)
    return result


def capitalize_default(a, **kwargs):  # pylint: disable=unused-argument
    ensure_definition(a)
    if not isinstance(a, str):
        a = str(a)
    if a and len(a) > 1:
        return a[0].upper() + a[1:]
    return a


def currency_symbol_default(**kwargs):  # pylint: disable=unused-argument
    """Returns the currency symbol for the current locale."""
    return str(locale.localeconv()['currency_symbol'])


def currency_default(the_value, **kwargs):
    """Returns the value as a currency, according to the conventions of
    the current locale.  Use the optional keyword argument
    decimals=False if you do not want to see decimal places in the
    number, and the optional currency_symbol for a different symbol
    than the default.

    """
    decimals = kwargs.get('decimals', True)
    symbol = kwargs.get('symbol', None)
    symbol_precedes = kwargs.get('symbol_precedes', None)
    ensure_definition(the_value, decimals, symbol)
    obj_type = type(the_value).__name__
    if obj_type in ['FinancialList', 'PeriodicFinancialList']:
        the_value = the_value.total()
    elif obj_type in ['Value', 'PeriodicValue']:
        if the_value.exists:
            the_value = the_value.amount()
        else:
            the_value = 0
    elif obj_type == 'DACatchAll':
        the_value = float(the_value)
    try:
        float(the_value)
    except:
        return ''
    the_float_value = float(the_value)
    the_symbol = None
    if symbol is not None:
        the_symbol = symbol
    elif 'locale_overrides' in this_thread.misc and 'currency_symbol' in this_thread.misc['locale_overrides']:
        the_symbol = this_thread.misc['locale_overrides']['currency_symbol']
    elif language_functions['currency_symbol']['*'] is not currency_symbol_default:
        the_symbol = currency_symbol()
    the_symbol_precedes = None
    if symbol_precedes is not None:
        the_symbol_precedes = symbol_precedes
    elif 'locale_overrides' in this_thread.misc and the_float_value < 0 and 'n_cs_precedes' in this_thread.misc['locale_overrides']:
        the_symbol_precedes = bool(this_thread.misc['locale_overrides']['n_cs_precedes'])
    elif 'locale_overrides' in this_thread.misc and 'p_cs_precedes' in this_thread.misc['locale_overrides']:
        the_symbol_precedes = bool(this_thread.misc['locale_overrides']['p_cs_precedes'])
    if the_symbol is None and the_symbol_precedes is None and decimals:
        return str(locale.currency(the_float_value, symbol=True, grouping=True))
    if the_symbol is None:
        the_symbol = currency_symbol()
    if the_symbol_precedes is None:
        if the_float_value < 0:
            the_symbol_precedes = bool(get_locale('n_cs_precedes'))
        else:
            the_symbol_precedes = bool(get_locale('p_cs_precedes'))
    output = ''
    if the_symbol_precedes:
        output += the_symbol
        if the_float_value < 0:
            if get_locale('n_sep_by_space'):
                output += ' '
        elif get_locale('p_sep_by_space'):
            output += ' '
    if decimals:
        output += locale.format_string('%.' + str(server.daconfig.get('currency decimal places', locale.localeconv()['frac_digits'])) + 'f', the_float_value, grouping=True, monetary=True)
    else:
        output += locale.format_string("%d", int(the_float_value), grouping=True, monetary=True)
    if not the_symbol_precedes:
        if the_float_value < 0:
            if get_locale('n_sep_by_space'):
                output += ' '
        elif get_locale('p_sep_by_space'):
            output += ' '
        output += the_symbol
    return output


def prefix_constructor(prefix):

    def func(the_word, **kwargs):
        ensure_definition(the_word, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(str(prefix)) + str(the_word)
        return str(prefix) + str(the_word)
    return func


def double_prefix_constructor_reverse(prefix_one, prefix_two):

    def func(word_one, word_two, **kwargs):
        ensure_definition(word_one, word_two, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(str(prefix_one)) + str(word_two) + str(prefix_two) + str(word_one)
        return str(prefix_one) + str(word_two) + str(prefix_two) + str(word_one)
    return func


def prefix_constructor_two_arguments(prefix, **kwargs):  # pylint: disable=unused-argument

    def func(word_one, word_two, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(str(prefix)) + str(word_one) + ' ' + str(word_two)
        return str(prefix) + str(word_one) + ' ' + str(word_two)
    return func


def middle_constructor(middle, **kwargs):  # pylint: disable=unused-argument

    def func(a, b, **kwargs):
        ensure_definition(a, b, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(str(a)) + str(middle) + str(b)
        return str(a) + str(middle) + str(b)
    return func


def possessify_en(a, b, **kwargs):
    ensure_definition(a, b, **kwargs)
    if this_thread.evaluation_context == 'docx':
        apostrophe = "’"
    else:
        apostrophe = "'"
    if 'plural' in kwargs and kwargs['plural']:
        middle = apostrophe + " "
    else:
        middle = apostrophe + "s "
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(str(a)) + str(middle) + str(b)
    return str(a) + str(middle) + str(b)


def a_preposition_b_default(a, b, **kwargs):
    ensure_definition(a, b, **kwargs)
    if hasattr(a, 'preposition'):
        preposition = word(a.preposition)
    else:
        preposition = word('in the')
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(str(a)) + str(' ' + preposition + ' ') + str(b)
    return str(a) + str(' ' + preposition + ' ') + str(b)


def verb_present_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    output = pattern_en.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    output = pattern_en.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def number_or_length(target):
    if isinstance(target, (int, float)):
        return target
    if isinstance(target, (list, dict, set, tuple)) or (hasattr(target, 'elements') and isinstance(target.elements, (list, dict, set))):
        return len(target)
    if target:
        return 2
    return 1


def noun_plural_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_en(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_en.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_en.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_en.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_present_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    if new_args[1] == 'pl':
        new_args[1] = '3pl'
    output = pattern_es.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    if new_args[1] == 'ppl':
        new_args[1] = '3ppl'
    output = pattern_es.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_plural_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_es(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_es.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_es.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_es.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_present_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    if new_args[1] == 'pl':
        new_args[1] = '3pl'
    output = pattern_de.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    if new_args[1] == 'ppl':
        new_args[1] = '3ppl'
    output = pattern_de.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_plural_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_de(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_de.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_de.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_de.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_present_fr(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    if new_args[1] == 'pl':
        new_args[1] = '3pl'
    output = pattern_fr.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_fr(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    if new_args[1] == 'ppl':
        new_args[1] = '3ppl'
    output = pattern_fr.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_plural_fr(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_fr(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_fr.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_fr(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_fr.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_fr(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_fr.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_present_it(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    if new_args[1] == 'pl':
        new_args[1] = '3pl'
    output = pattern_it.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_it(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    if new_args[1] == 'ppl':
        new_args[1] = '3ppl'
    output = pattern_it.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_plural_it(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_it(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_it.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_it(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_it.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_it(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_it.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_present_nl(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    if new_args[1] == 'pl':
        new_args[1] = '3pl'
    output = pattern_nl.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_nl(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    if new_args[1] == 'ppl':
        new_args[1] = '3ppl'
    output = pattern_nl.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_plural_nl(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_nl(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_nl.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_nl(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_nl.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_nl(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_nl.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def titlecasestr(text):
    return titlecase.titlecase(str(text))

language_functions = {
    'in_the': {
        'en': prefix_constructor('in the ')
    },
    'a_preposition_b': {
        'en': a_preposition_b_default
    },
    'a_in_the_b': {
        'en': middle_constructor(' in the ')
    },
    'i_subjective': {
        'en': lambda *pargs, **kwargs: word('I', **kwargs)
    },
    'he_subjective': {
        'en': lambda *pargs, **kwargs: word('he', **kwargs)
    },
    'she_subjective': {
        'en': lambda *pargs, **kwargs: word('she', **kwargs)
    },
    'genderless_subjective': {
        'en': lambda *pargs, **kwargs: word('they', **kwargs)
    },
    'myself': {
        'en': lambda *pargs, **kwargs: word('myself', **kwargs)
    },
    'itself': {
        'en': lambda *pargs, **kwargs: word('itself', **kwargs)
    },
    'herself': {
        'en': lambda *pargs, **kwargs: word('herself', **kwargs)
    },
    'himself': {
        'en': lambda *pargs, **kwargs: word('himself', **kwargs)
    },
    'themselves': {
        'en': lambda *pargs, **kwargs: word('themselves', **kwargs)
    },
    'genderless_self': {
        'en': lambda *pargs, **kwargs: word('themself', **kwargs)
    },
    'yourself': {
        'en': lambda *pargs, **kwargs: word('yourself', **kwargs)
    },
    'yourselves': {
        'en': lambda *pargs, **kwargs: word('yourselves', **kwargs)
    },
    'ourselves': {
        'en': lambda *pargs, **kwargs: word('ourselves', **kwargs)
    },
    'you_subjective': {
        'en': lambda *pargs, **kwargs: word('you', **kwargs)
    },
    'you_subjective_plural': {
        'en': lambda *pargs, **kwargs: word('you', **kwargs)
    },
    'we_subjective': {
        'en': lambda *pargs, **kwargs: word('we', **kwargs)
    },
    'they_subjective': {
        'en': lambda *pargs, **kwargs: word('they', **kwargs)
    },
    'it_subjective': {
        'en': lambda *pargs, **kwargs: word('it', **kwargs)
    },
    'it_objective': {
        'en': lambda *pargs, **kwargs: word('it', **kwargs)
    },
    'them_objective': {
        'en': lambda *pargs, **kwargs: word('them', **kwargs)
    },
    'genderless_objective': {
        'en': lambda *pargs, **kwargs: word('them', **kwargs)
    },
    'me_objective': {
        'en': lambda *pargs, **kwargs: word('me', **kwargs)
    },
    'him_objective': {
        'en': lambda *pargs, **kwargs: word('him', **kwargs)
    },
    'her_objective': {
        'en': lambda *pargs, **kwargs: word('her', **kwargs)
    },
    'you_objective': {
        'en': lambda *pargs, **kwargs: word('you', **kwargs)
    },
    'you_objective_plural': {
        'en': lambda *pargs, **kwargs: word('you', **kwargs)
    },
    'us_objective': {
        'en': lambda *pargs, **kwargs: word('us', **kwargs)
    },
    'are_we': {
        'en': lambda *pargs, **kwargs: word('are we', **kwargs)
    },
    'are_you': {
        'en': lambda *pargs, **kwargs: word('are you', **kwargs)
    },
    'are_you_plural': {
        'en': lambda *pargs, **kwargs: word('are you', **kwargs)
    },
    'am_i': {
        'en': lambda *pargs, **kwargs: word('am I', **kwargs)
    },
    'her': {
        'en': prefix_constructor('her ')
    },
    'his': {
        'en': prefix_constructor('his ')
    },
    'are_word': {
        'en': prefix_constructor('are ')
    },
    'is_word': {
        'en': prefix_constructor('is ')
    },
    'their': {
        'en': prefix_constructor('their ')
    },
    'my_possessive': {
        'en': prefix_constructor('my ')
    },
    'our_possessive': {
        'en': prefix_constructor('our ')
    },
    'of_the': {
        'en': prefix_constructor('of the ')
    },
    'your': {
        'en': prefix_constructor('your ')
    },
    'your_plural': {
        'en': prefix_constructor('your ')
    },
    'some': {
        'en': prefix_constructor('some ')
    },
    'its': {
        'en': prefix_constructor('its ')
    },
    'the': {
        'en': prefix_constructor('the ')
    },
    'these': {
        'en': prefix_constructor('these ')
    },
    'this': {
        'en': prefix_constructor('this ')
    },
    'does_a_b': {
        'en': prefix_constructor_two_arguments('does ')
    },
    'do_a_b': {
        'en': prefix_constructor_two_arguments('do ')
    },
    'did_a_b': {
        'en': prefix_constructor_two_arguments('did ')
    },
    'did_a_b_plural': {
        'en': prefix_constructor_two_arguments('did ')
    },
    'do_i': {
        'en': prefix_constructor('do I ')
    },
    'do_we': {
        'en': prefix_constructor('do we ')
    },
    'do_you': {
        'en': prefix_constructor('do you ')
    },
    'do_you_plural': {
        'en': prefix_constructor('do you ')
    },
    'did_i': {
        'en': prefix_constructor('did I ')
    },
    'did_we': {
        'en': prefix_constructor('did we ')
    },
    'did_you': {
        'en': prefix_constructor('did you ')
    },
    'did_you_plural': {
        'en': prefix_constructor('did you ')
    },
    'was_i': {
        'en': prefix_constructor('was I ')
    },
    'were_we': {
        'en': prefix_constructor('were we ')
    },
    'were_you': {
        'en': prefix_constructor('were you ')
    },
    'were_you_plural': {
        'en': prefix_constructor('were you ')
    },
    'was_a_b': {
        'en': prefix_constructor_two_arguments('was ')
    },
    'were_a_b': {
        'en': prefix_constructor_two_arguments('were ')
    },
    'were_a_b_plural': {
        'en': prefix_constructor_two_arguments('were ')
    },
    'have_i': {
        'en': prefix_constructor('have I ')
    },
    'have_we': {
        'en': prefix_constructor('have we ')
    },
    'have_you': {
        'en': prefix_constructor('have you ')
    },
    'have_you_plural': {
        'en': prefix_constructor('have you ')
    },
    'has_a_b': {
        'en': prefix_constructor_two_arguments('has ')
    },
    'have_a_b': {
        'en': prefix_constructor_two_arguments('have ')
    },
    'verb_past': {
        'en': verb_past_en,
        'es': verb_past_es,
        'de': verb_past_de,
        'fr': verb_past_fr,
        'it': verb_past_it,
        'nl': verb_past_nl
    },
    'verb_present': {
        'en': verb_present_en,
        'es': verb_present_es,
        'de': verb_present_de,
        'fr': verb_present_fr,
        'it': verb_present_it,
        'nl': verb_present_nl
    },
    'noun_plural': {
        'en': noun_plural_en,
        'es': noun_plural_es,
        'de': noun_plural_de,
        'fr': noun_plural_fr,
        'it': noun_plural_it,
        'nl': noun_plural_nl
    },
    'noun_singular': {
        'en': noun_singular_en,
        'es': noun_singular_es,
        'de': noun_singular_de,
        'fr': noun_singular_fr,
        'it': noun_singular_it,
        'nl': noun_singular_nl
    },
    'indefinite_article': {
        'en': indefinite_article_en,
        'es': indefinite_article_es,
        'de': indefinite_article_de,
        'it': indefinite_article_it
    },
    'currency_symbol': {
        '*': currency_symbol_default
    },
    'period_list': {
        '*': lambda: [[12, word("Per Month")], [1, word("Per Year")], [52, word("Per Week")], [24, word("Twice Per Month")], [26, word("Every Two Weeks")]]
    },
    'name_suffix': {
        '*': lambda: ['Jr', 'Sr', 'II', 'III', 'IV', 'V', 'VI']
    },
    'currency': {
        '*': currency_default
    },
    'possessify': {
        'en': possessify_en
    },
    'possessify_long': {
        'en': double_prefix_constructor_reverse('the ', ' of the ')
    },
    'comma_and_list': {
        'en': comma_and_list_en,
        'es': comma_and_list_es,
        'de': comma_and_list_de
    },
    'comma_list': {
        'en': comma_list_en
    },
    'add_separators': {
        'en': add_separators_en
    },
    'nice_number': {
        '*': nice_number_default
    },
    'quantity_noun': {
        '*': quantity_noun_default
    },
    'ordinal_number': {
        '*': ordinal_number_default
    },
    'ordinal': {
        '*': ordinal_default
    },
    'capitalize': {
        '*': capitalize_default
    },
    'title_case': {
        '*': titlecasestr
    },
    'salutation': {
        '*': salutation_default
    }
}


def language_function_constructor(term):

    def func(*args, **kwargs):
        ensure_definition(*args, **kwargs)
        language = kwargs.get('language', None)
        if language is None:
            language = this_thread.language
        if language in language_functions[term]:
            return language_functions[term][language](*args, **kwargs)
        if '*' in language_functions[term]:
            return language_functions[term]['*'](*args, **kwargs)
        if 'en' in language_functions[term]:
            logmessage("Term " + str(term) + " is not defined for language " + str(language))
            return language_functions[term]['en'](*args, **kwargs)
        raise SystemError("term " + str(term) + " not defined in language_functions for English or *")
    return func

in_the = language_function_constructor('in_the')
a_preposition_b = language_function_constructor('a_preposition_b')
a_in_the_b = language_function_constructor('a_in_the_b')
i_subjective = language_function_constructor('i_subjective')
he_subjective = language_function_constructor('he_subjective')
she_subjective = language_function_constructor('she_subjective')
genderless_subjective = language_function_constructor('genderless_subjective')
myself = language_function_constructor('myself')
itself = language_function_constructor('itself')
herself = language_function_constructor('herself')
himself = language_function_constructor('himself')
themselves = language_function_constructor('themselves')
genderless_self = language_function_constructor('genderless_self')
yourself = language_function_constructor('yourself')
yourselves = language_function_constructor('yourselves')
ourselves = language_function_constructor('ourselves')
you_subjective = language_function_constructor('you_subjective')
you_subjective_plural = language_function_constructor('you_subjective_plural')
we_subjective = language_function_constructor('we_subjective')
they_subjective = language_function_constructor('they_subjective')
it_subjective = language_function_constructor('it_subjective')
it_objective = language_function_constructor('it_objective')
them_objective = language_function_constructor('them_objective')
genderless_objective = language_function_constructor('genderless_objective')
me_objective = language_function_constructor('me_objective')
him_objective = language_function_constructor('him_objective')
her_objective = language_function_constructor('her_objective')
you_objective = language_function_constructor('you_objective')
you_objective_plural = language_function_constructor('you_objective_plural')
us_objective = language_function_constructor('us_objective')
are_we = language_function_constructor('are_we')
are_you = language_function_constructor('are_you')
are_you_plural = language_function_constructor('are_you_plural')
am_i = language_function_constructor('am_i')
her = language_function_constructor('her')
his = language_function_constructor('his')
are_word = language_function_constructor('are_word')
is_word = language_function_constructor('is_word')
their = language_function_constructor('their')
my_possessive = language_function_constructor('my_possessive')
our_possessive = language_function_constructor('our_possessive')
of_the = language_function_constructor('of_the')
your = language_function_constructor('your')
your_plural = language_function_constructor('your_plural')
some = language_function_constructor('some')
its = language_function_constructor('its')
the = language_function_constructor('the')
these = language_function_constructor('these')
this = language_function_constructor('this')
does_a_b = language_function_constructor('does_a_b')
do_a_b = language_function_constructor('do_a_b')
did_a_b = language_function_constructor('did_a_b')
did_a_b_plural = language_function_constructor('did_a_b_plural')
do_i = language_function_constructor('do_i')
do_we = language_function_constructor('do_we')
do_you = language_function_constructor('do_you')
do_you_plural = language_function_constructor('do_you_plural')
did_i = language_function_constructor('did_i')
did_we = language_function_constructor('did_we')
did_you = language_function_constructor('did_you')
did_you_plural = language_function_constructor('did_you_plural')
was_i = language_function_constructor('was_i')
were_we = language_function_constructor('were_we')
were_you = language_function_constructor('were_you')
were_you_plural = language_function_constructor('were_you_plural')
was_a_b = language_function_constructor('was_a_b')
were_a_b = language_function_constructor('were_a_b')
were_a_b_plural = language_function_constructor('were_a_b_plural')
have_i = language_function_constructor('have_i')
have_we = language_function_constructor('have_we')
have_you = language_function_constructor('have_you')
have_you_plural = language_function_constructor('have_you_plural')
has_a_b = language_function_constructor('has_a_b')
have_a_b = language_function_constructor('have_a_b')
verb_past = language_function_constructor('verb_past')
verb_present = language_function_constructor('verb_present')
noun_plural = language_function_constructor('noun_plural')
noun_singular = language_function_constructor('noun_singular')
indefinite_article = language_function_constructor('indefinite_article')
period_list = language_function_constructor('period_list')
name_suffix = language_function_constructor('name_suffix')
currency = language_function_constructor('currency')
currency_symbol = language_function_constructor('currency_symbol')
possessify = language_function_constructor('possessify')
possessify_long = language_function_constructor('possessify_long')
comma_list = language_function_constructor('comma_list')
comma_and_list = language_function_constructor('comma_and_list')
add_separators = language_function_constructor('add_separators')
nice_number = language_function_constructor('nice_number')
quantity_noun = language_function_constructor('quantity_noun')
capitalize = language_function_constructor('capitalize')
capitalize_function = capitalize
title_case = language_function_constructor('title_case')
ordinal_number = language_function_constructor('ordinal_number')
ordinal = language_function_constructor('ordinal')
salutation = language_function_constructor('salutation')

if verb_past.__doc__ is None:
    verb_past.__doc__ = """Return the past tense of a verb.

    Args:
        verb (str): The verb to conjugate.
        **kwargs: Optional conjugation parameters passed to the underlying
            language function (e.g. ``'3gp'`` for third-person past tense).

    Returns:
        str: The past-tense form of the verb (e.g. ``verb_past('help')``
            returns ``'helped'``).
    """
if verb_present.__doc__ is None:
    verb_present.__doc__ = """Return the present tense of a verb.

    Args:
        verb (str): The verb to conjugate (may be in any tense).
        **kwargs: Optional conjugation parameters passed to the underlying
            language function (e.g. ``'3sg'`` for third-person singular).

    Returns:
        str: The present-tense form of the verb (e.g.
            ``verb_present('helped', '3sg')`` returns ``'helps'``).
    """
if noun_plural.__doc__ is None:
    noun_plural.__doc__ = """Return the plural form of a noun.

    Args:
        noun (str): The noun to pluralize.
        *pargs: An optional quantity (number, list, dict, or set). When the
            quantity is exactly ``1`` the singular form is returned instead.
        **kwargs: Pass ``noun_is_singular=True`` to skip singularization
            before pluralizing.

    Returns:
        str: The plural form of the noun, or the singular form if the
            optional quantity equals ``1``.
    """
if noun_singular.__doc__ is None:
    noun_singular.__doc__ = """Return the singular form of a noun.

    Args:
        noun (str): The noun to singularize.
        *pargs: An optional quantity (number, list, dict, or set). When the
            quantity is not ``1`` the original noun is returned unchanged.

    Returns:
        str: The singular form of the noun, or the original noun when the
            optional quantity is not ``1``.
    """
if indefinite_article.__doc__ is None:
    indefinite_article.__doc__ = """Return a noun preceded by the appropriate indefinite article.

    Args:
        noun (str): The noun phrase to precede with an article.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: The noun prefixed with ``'a'`` or ``'an'`` as appropriate
            (e.g. ``indefinite_article('apple')`` returns ``'an apple'``).
    """
if capitalize.__doc__ is None:
    capitalize.__doc__ = """Return the input string with the first letter capitalized.

    Args:
        a (str): The string to capitalize.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: The input string with its first character converted to
            upper case.
    """
if period_list.__doc__ is None:
    period_list.__doc__ = """Return a list of per-year period options for use in multiple-choice fields.

    Returns:
        list: A list of ``[number, label]`` pairs representing common
            payment periods (e.g. ``[[12, 'Per Month'], [1, 'Per Year'],
            [52, 'Per Week'], ...]``).
    """
if name_suffix.__doc__ is None:
    name_suffix.__doc__ = """Return a list of common name suffixes for use in multiple-choice fields.

    Returns:
        list: A list of name suffix strings such as
            ``['Jr', 'Sr', 'II', 'III', 'IV', 'V', 'VI']``.
    """
if currency.__doc__ is None:
    currency.__doc__ = """Format a number as a currency value using the current locale.

    Args:
        value: The numeric value to format.
        **kwargs: Optional keyword arguments including ``decimals`` (bool,
            default ``True``), ``symbol`` (str override for the currency
            symbol), and ``symbol_precedes`` (bool controlling symbol
            position).

    Returns:
        str: The formatted currency string (e.g. ``currency(45.2)`` returns
            ``'$45.20'`` for a US locale).
    """
if currency_symbol.__doc__ is None:
    currency_symbol.__doc__ = """Return the currency symbol for the current locale.

    Returns:
        str: The currency symbol (e.g. ``'$'`` for a US locale). Respects
            overrides set via :func:`set_locale` or the ``currency symbol``
            configuration setting.
    """
if possessify.__doc__ is None:
    possessify.__doc__ = """Return the possessive phrase combining two arguments.

    Args:
        a: The possessor.
        b: The thing possessed.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: A possessive phrase such as ``"a's b"``.
    """
if possessify_long.__doc__ is None:
    possessify_long.__doc__ = """Return the long possessive phrase combining two arguments.

    Args:
        a: The possessor.
        b: The thing possessed.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: A possessive phrase of the form ``"the b of a"``.
    """
if comma_list.__doc__ is None:
    comma_list.__doc__ = """Return the items joined by commas.

    Args:
        *pargs: Items to join, or a single iterable as the first argument.
        **kwargs: Optional ``comma_string`` (default ``', '``) to customize
            the separator.

    Returns:
        str: The items separated by commas (e.g.
            ``comma_list('lions', 'tigers', 'bears')`` returns
            ``'lions, tigers, bears'``).
    """
if comma_and_list.__doc__ is None:
    comma_and_list.__doc__ = """Return the items joined by commas with "and" before the last item.

    Args:
        *pargs: Items to join, or a single iterable as the first argument.
        **kwargs: Optional keyword arguments including ``oxford`` (bool,
            default ``True``), ``and_string`` (default ``'and'``),
            ``comma_string``, ``before_and``, and ``after_and``.

    Returns:
        str: An English-language listing such as ``'lions, tigers, and
            bears'``.
    """
if add_separators.__doc__ is None:
    add_separators.__doc__ = """Return the list items as strings with separators appended.

    Appends ``;`` to all items except the penultimate, which gets
    ``'; and'``, and the last, which gets ``'.'``.

    Args:
        the_list: The list of items to process.
        separator (str, optional): Separator appended to middle items.
            Defaults to ``';'``.
        last_separator (str, optional): Separator appended to the
            penultimate item. Defaults to ``'; and'``.
        end_mark (str, optional): Mark appended to the final item.
            Defaults to ``'.'``.

    Returns:
        list: A list of strings with separators appended.
    """
if nice_number.__doc__ is None:
    nice_number.__doc__ = """Return a number expressed as a word for small values, or as a formatted numeral.

    Args:
        num: The number to convert.
        **kwargs: Optional keyword arguments including ``capitalize``
            (bool), ``language`` (str), and ``use_word`` (bool, default
            ``False``).

    Returns:
        str: The number as a word (e.g. ``nice_number(4)`` returns
            ``'four'``) or as a locale-formatted numeral for larger values.
    """
if quantity_noun.__doc__ is None:
    quantity_noun.__doc__ = """Return a number combined with a noun in the appropriate singular or plural form.

    Combines :func:`nice_number` and :func:`noun_plural`. Rounds the number
    to the nearest integer unless ``as_integer=False`` is passed.

    Args:
        num: The quantity.
        noun (str): The singular noun.
        **kwargs: Optional keyword arguments including ``as_integer``
            (bool, default ``True``) and other arguments accepted by
            :func:`nice_number`.

    Returns:
        str: The quantity and noun combined (e.g. ``quantity_noun(2,
            'apple')`` returns ``'two apples'``).
    """
if title_case.__doc__ is None:
    title_case.__doc__ = """Return the input string with the first letter of each word capitalized.

    Args:
        a (str): The string to convert to title case.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: The title-cased string (e.g. ``title_case('the importance of
            being ernest')`` returns ``'The Importance of Being Ernest'``).
    """
if ordinal_number.__doc__ is None:
    ordinal_number.__doc__ = """Return the ordinal form of a cardinal number.

    Args:
        num: The cardinal number (1-based).
        **kwargs: Optional keyword arguments including ``capitalize``
            (bool) and ``use_word`` (bool, default depends on the value).

    Returns:
        str: The ordinal form (e.g. ``ordinal_number(8)`` returns
            ``'eighth'``; ``ordinal_number(8, use_word=False)`` returns
            ``'8th'``).
    """
if ordinal.__doc__ is None:
    ordinal.__doc__ = """Return the ordinal form of a zero-based index.

    Equivalent to ``ordinal_number(num + 1)``. This is useful when working
    with zero-based list indexes.

    Args:
        num: The zero-based index.
        **kwargs: Optional keyword arguments passed to :func:`ordinal_number`.

    Returns:
        str: The ordinal form (e.g. ``ordinal(0)`` returns ``'first'``;
            ``ordinal(22)`` returns ``'23rd'``).
    """


def underscore_to_space(a):
    return re.sub('_', ' ', str(a))


def space_to_underscore(a):
    """Convert spaces to underscores and sanitize the input for use as a filename.

    Replaces spaces with underscores and removes characters that are not safe
    for filenames using Werkzeug's ``secure_filename``.

    Args:
        a: The value to convert (coerced to a string).

    Returns:
        str: A filename-safe string with spaces replaced by underscores.
    """
    return werkzeug.utils.secure_filename(str(a).encode('ascii', errors='ignore').decode())


def message(*pargs, **kwargs):
    """Stop the interview and present a message screen to the user.

    Raises a ``QuestionError`` so that docassemble immediately shows a screen
    with the given title and optional subquestion text.  Code after
    ``message()`` is never executed.

    Args:
        *pargs: Positional arguments passed to the underlying
            ``QuestionError``.  The first argument is the title
            (``question``) and the optional second argument is the body
            (``subquestion``).
        **kwargs: Keyword arguments such as ``question``, ``subquestion``,
            ``show_restart``, ``show_exit``, ``show_leave``, ``url``, and
            ``buttons``.
    """
    raise QuestionError(*pargs, **kwargs)


def response(*pargs, **kwargs):
    """Send a custom HTTP response instead of the normal interview screen.

    Raises a ``ResponseError`` so that docassemble immediately returns the
    specified content to the client.  Code after ``response()`` is never
    executed.

    Args:
        *pargs: Positional arguments passed to the underlying
            ``ResponseError``.
        **kwargs: Keyword arguments specifying the response type and
            content.  Use one of: ``response`` (text), ``binaryresponse``
            (bytes), ``file`` (``DAFile`` or package reference), or ``url``
            (redirect target).  Optional: ``content_type`` and
            ``response_code`` (default ``200``).
    """
    raise ResponseError(*pargs, **kwargs)


def json_response(data, response_code=None):
    """Send the given data as a JSON HTTP response.

    A shorthand for calling :func:`response` with a JSON-encoded binary
    body and ``content_type='application/json'``.  Code after
    ``json_response()`` is never executed.

    Args:
        data: The data to serialize and return as JSON.
        response_code (int, optional): The HTTP response code. Defaults to
            ``200``.
    """
    raise ResponseError(binaryresponse=(json.dumps(data, sort_keys=True, indent=2) + "\n").encode('utf-8'), content_type="application/json", response_code=response_code)


def variables_as_json(include_internal=False):
    """Send all interview session variables as a JSON HTTP response.

    Like :func:`all_variables` combined with :func:`json_response`: returns
    all interview variables in simplified, JSON-serializable form.  Code
    after ``variables_as_json()`` is never executed.

    Args:
        include_internal (bool, optional): If ``True``, includes the
            ``_internal`` and ``nav`` variables in the output. Defaults to
            ``False``.
    """
    raise ResponseError(None, all_variables=True, include_internal=include_internal)


def store_variables_snapshot(data=None, include_internal=False, key=None, persistent=False):
    """Store a snapshot of the interview answers in unencrypted JSON format.

    Writes the current interview variables (or provided ``data``) to the
    database in plain JSON so they can be retrieved later without the user's
    encryption key.

    Args:
        data (optional): Data to store instead of the current interview
            variables. Defaults to ``None`` (uses current interview
            variables).
        include_internal (bool, optional): If ``True``, includes
            ``_internal`` variables in the snapshot. Defaults to ``False``.
        key (str, optional): A tag string to associate with the snapshot.
            Defaults to ``None``.
        persistent (bool, optional): If ``True``, the snapshot persists
            after the session ends. Defaults to ``False``.
    """
    session = get_uid()
    filename = this_thread.current_info.get('yaml_filename', None)
    if session is None or filename is None:
        raise DAError("store_variables_snapshot: could not identify the session")
    if key is not None and not isinstance(key, str):
        raise DAError("store_variables_snapshot: key must be a string")
    if data is None:
        the_data = serializable_dict(get_user_dict(), include_internal=include_internal)
    else:
        the_data = safe_json(data)
    server.write_answer_json(session, filename, the_data, tags=key, persistent=bool(persistent))


def all_variables(simplify=True, include_internal=False, special=False, make_copy=False):
    """Return the interview session variables as a dictionary.

    By default, returns a simplified dictionary suitable for JSON
    serialization (objects converted to dicts, dates to ISO strings).
    Use ``simplify=False`` for the raw Python dictionary.

    Args:
        simplify (bool, optional): If ``True`` (default), converts objects
            to JSON-friendly representations. If ``False``, returns the raw
            Python dictionary.
        include_internal (bool, optional): If ``True``, includes the
            ``_internal`` and ``nav`` variables. Defaults to ``False``.
        special (str or bool, optional): Pass ``'titles'`` to return
            interview title metadata, ``'metadata'`` to return consolidated
            metadata, or ``'tags'`` to return the current session tags.
            Defaults to ``False``.
        make_copy (bool, optional): When ``simplify=False``, if ``True``
            returns a deep copy of the dictionary. Defaults to ``False``.

    Returns:
        dict or set: The interview variables dictionary, or a set of tags
            when ``special='tags'``.
    """
    if special == 'titles':
        return this_thread.interview.get_title(get_user_dict(), adapted=True)
    if special == 'metadata':
        return copy.deepcopy(this_thread.interview.consolidated_metadata)
    if special == 'tags':
        session_tags()
        return copy.deepcopy(this_thread.internal['tags'])
    if simplify:
        return serializable_dict(get_user_dict(), include_internal=include_internal)
    if make_copy:
        new_dict = copy.deepcopy(pickleable_objects(get_user_dict()))
    else:
        new_dict = pickleable_objects(get_user_dict())
    if not include_internal and '_internal' in new_dict:
        new_dict = copy.copy(new_dict)
        del new_dict['_internal']
    return new_dict


def command(*pargs, **kwargs):
    """Trigger an interview exit command such as exit, logout, or restart.

    Raises a ``CommandError`` so that docassemble immediately processes the
    specified command.  Code after ``command()`` is never executed.

    Args:
        *pargs: The command string as the first positional argument.  Valid
            values are ``'restart'``, ``'new_session'``, ``'exit'``,
            ``'logout'``, ``'exit_logout'``, ``'leave'``, and
            ``'signin'``.
        **kwargs: Optional keyword arguments such as ``url`` (the redirect
            target) and ``sleep`` (seconds to pause in scheduled tasks).
    """
    raise CommandError(*pargs, **kwargs)


def unpack_pargs(args):
    the_list = []
    for parg in args:
        if isinstance(parg, (types.GeneratorType, map, filter)):
            for sub_parg in parg:
                the_list.append(sub_parg)
        else:
            the_list.append(parg)
    return the_list


def force_ask(*pargs, **kwargs):
    """Force docassemble to ask one or more questions, even if the variables are already defined.

    Triggers the actions mechanism so that the interview shows a question
    corresponding to each specified variable name, regardless of whether the
    variable is already defined.  Code after ``force_ask()`` is never reached.
    Variable names must be passed as strings.

    Args:
        *pargs: Variable name strings (or action dictionaries) identifying
            the questions to ask.
        **kwargs: Optional keyword arguments including ``forget_prior``
            (bool, default ``False``) to clear pending actions before
            adding new ones, and ``evaluate`` (bool, default ``False``) to
            resolve alias variable names to their intrinsic names.
    """
    the_pargs = unpack_pargs(pargs)
    if kwargs.get('forget_prior', False):
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack']:
            this_thread.internal['event_stack'][unique_id] = []
    if kwargs.get('persistent', True):
        for item in the_pargs:
            if isinstance(item, str) and illegal_variable_name(item):
                raise DAError("Illegal variable name")
        raise ForcedNameError(*the_pargs, user_dict=get_user_dict(), evaluate=kwargs.get('evaluate', False))
    force_ask_nameerror(the_pargs[0])


def force_ask_nameerror(variable_name, priority=False):  # pylint: disable=unused-argument
    if illegal_variable_name(variable_name):
        raise DAError("Illegal variable name")
    raise DANameError("name '" + str(variable_name) + "' is not defined")


def force_gather(*pargs, forget_prior=False, evaluate=False):
    """Force docassemble to keep seeking a definition for one or more variables.

    Unlike :func:`force_ask`, this function affects the global interview
    logic (for all users) and does not require the variable to be
    undefined.  It adds each variable to an internal gather list so that
    :func:`process_action` continues to seek its definition until it is
    defined.  Code after ``force_gather()`` is never reached.

    Args:
        *pargs: Variable name strings identifying the variables to gather.
        forget_prior (bool, optional): If ``True``, clears any pending
            actions before adding the new ones. Defaults to ``False``.
        evaluate (bool, optional): If ``True``, resolves alias variable
            names to their intrinsic names before gathering. Defaults to
            ``False``.
    """
    if forget_prior:
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack']:
            this_thread.internal['event_stack'][unique_id] = []
    the_user_dict = get_user_dict()
    the_context = {}
    for var_name in ('x', 'i', 'j', 'k', 'l', 'm', 'n'):
        if var_name in the_user_dict:
            the_context[var_name] = the_user_dict[var_name]
    last_variable_name = None
    pargs = unpack_pargs(pargs)
    if evaluate:
        pargs = intrinsic_names_of(*pargs, the_user_dict=the_user_dict)
    for variable_name in pargs:
        if variable_name not in [(variable_dict if isinstance(variable_dict, str) else variable_dict['var']) for variable_dict in this_thread.internal['gather']]:
            this_thread.internal['gather'].append({'var': variable_name, 'context': the_context})
        last_variable_name = variable_name
    if last_variable_name is not None:
        if illegal_variable_name(last_variable_name):
            raise DAError("Illegal variable name")
        raise ForcedNameError(last_variable_name, gathering=True, user_dict=the_user_dict)


def static_filename_path(filereference, return_nonexistent=False):
    ensure_definition(filereference)
    if re.search(r'data/templates/', filereference):
        result = package_template_filename(filereference, return_nonexistent=return_nonexistent)
    else:
        result = package_data_filename(static_filename(filereference), return_nonexistent=return_nonexistent)
    # if result is None or not os.path.isfile(result):
    #    result = server.absolute_filename("/playgroundstatic/" + re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filereference)).path
    return result


def static_filename(filereference):
    # logmessage("static_filename: got " + filereference)
    ensure_definition(filereference)
    if re.search(r',', filereference):
        return None
    # filereference = re.sub(r'^None:data/static/', '', filereference)
    # filereference = re.sub(r'^None:', '', filereference)
    parts = filereference.split(':')
    if len(parts) < 2:
        parts = [this_thread.current_package, filereference]
        # parts = ['docassemble.base', filereference]
    if re.search(r'\.\./', parts[1]):
        return None
    if not re.match(r'(data|static)/.*', parts[1]):
        parts[1] = 'data/static/' + parts[1]
    # logmessage("static_filename: returning " + parts[0] + ':' + parts[1])
    return parts[0] + ':' + parts[1]


def static_image(filereference, width=None):
    """Return the markup string to embed a static image.

    Produces a ``[FILE ...]`` markup tag that docassemble renders as an
    image.  Useful when the image path is assembled programmatically
    rather than written literally in a template.

    Args:
        filereference (str): A package-qualified file reference such as
            ``'docassemble.demo:crawling.png'``, or just ``'crawling.png'``
            for a file in the current package.
        width (str, optional): The display width, e.g. ``'2in'`` or
            ``'50%'``. Defaults to ``None`` (no explicit width).

    Returns:
        str: A ``[FILE ...]`` markup string, or an error string if the
            reference is invalid.
    """
    ensure_definition(filereference, width)
    filename = static_filename(filereference)
    if filename is None:
        return 'ERROR: invalid image reference'
    if width is None:
        return '[FILE ' + filename + ']'
    return '[FILE ' + filename + ', ' + width + ']'


def qr_code(string, width=None, alt_text=None):
    """Return the markup string to embed a QR code image for the given string.

    Produces a ``[QR ...]`` markup tag that docassemble renders as a QR
    code image.  Useful when the string to encode is assembled
    programmatically rather than written literally in a template.

    Args:
        string (str): The text or URL to encode in the QR code.
        width (str, optional): The display width, e.g. ``'2in'``. Defaults
            to ``None`` (no explicit width).
        alt_text (str, optional): The alt text for the image. Defaults to
            ``None``.

    Returns:
        str: A ``[QR ...]`` markup string.
    """
    ensure_definition(string, width)
    if width is None:
        if alt_text is None:
            return '[QR ' + string + ']'
        return '[QR ' + string + ', None, ' + str(alt_text) + ']'
    if alt_text is None:
        return '[QR ' + string + ', ' + width + ']'
    return '[QR ' + string + ', ' + width + ', ' + str(alt_text) + ']'


def standard_template_filename(the_file, return_nonexistent=False):
    if filename_invalid(the_file):
        return None
    try:
        path = Path(importlib.resources.files('docassemble.base'), 'data', 'templates', str(the_file))
    except:
        return None
    if path.exists() or return_nonexistent:
        return str(path)
    # logmessage("Error retrieving data file")
    return None


def package_template_filename(the_file, **kwargs):
    the_file = the_file.strip()
    parts = the_file.split(":")
    if len(parts) == 1:
        package = kwargs.get('package', None)
        if package is not None:
            parts = [package, the_file]
    if len(parts) == 2:
        m = re.search(r'^docassemble\.playground([0-9]+)([A-Za-z]?[A-Za-z0-9]*)$', parts[0])
        if m:
            parts[1] = re.sub(r'^data/templates/', '', parts[1])
            abs_file = server.absolute_filename("/playgroundtemplate/" + m.group(1) + '/' + (m.group(2) or 'default') + '/' + re.sub(r'[^A-Za-z0-9\-\_\. ]', '', parts[1]))  # pylint: disable=assignment-from-none
            if abs_file is None:
                return None
            return abs_file.path
        if not re.match(r'data/.*', parts[1]):
            parts[1] = 'data/templates/' + parts[1]
        if filename_invalid(parts[1]) or package_name_invalid(parts[0]):
            return None
        try:
            path = Path(importlib.resources.files(parts[0]), parts[1])
        except:
            return None
        if path.exists() or kwargs.get('return_nonexistent', False):
            return str(path)
    return None


def standard_question_filename(the_file, return_nonexistent=False):
    if filename_invalid(the_file):
        return None
    try:
        path = Path(importlib.resources.files('docassemble.base'), 'data', 'questions', str(the_file))
    except:
        return None
    if path.exists() or return_nonexistent:
        return str(path)
    return None


def package_data_filename(the_file, return_nonexistent=False):
    # logmessage("package_data_filename with: " + str(the_file))
    if the_file is None:
        return None
    # the_file = re.sub(r'^None:data/static/', '', the_file)
    # the_file = re.sub(r'^None:', '', the_file)
    parts = the_file.split(":")
    result = None
    if len(parts) == 1:
        parts = [this_thread.current_package, the_file]
    #    parts = ['docassemble.base', the_file]
    if len(parts) == 2:
        if filename_invalid(parts[1]) or package_name_invalid(parts[0]):
            return None
        m = re.search(r'^docassemble\.playground([0-9]+)([A-Za-z]?[A-Za-z0-9]*)$', parts[0])
        if m:
            if re.search(r'^data/sources/', parts[1]):
                parts[1] = re.sub(r'^data/sources/', '', parts[1])
                abs_file = server.absolute_filename("/playgroundsources/" + m.group(1) + '/' + (m.group(2) or 'default') + '/' + re.sub(r'[^A-Za-z0-9\-\_\. ]', '', parts[1]))  # pylint: disable=assignment-from-none
                if abs_file is None:
                    return None
                return abs_file.path
            parts[1] = re.sub(r'^data/static/', '', parts[1])
            abs_file = server.absolute_filename("/playgroundstatic/" + m.group(1) + '/' + (m.group(2) or 'default') + '/' + re.sub(r'[^A-Za-z0-9\-\_\. ]', '', parts[1]))  # pylint: disable=assignment-from-none
            if abs_file is None:
                return None
            return abs_file.path
        if filename_invalid(parts[1]) or package_name_invalid(parts[0]):
            return None
        try:
            path = Path(importlib.resources.files(parts[0]), parts[1])
        except:
            return None
        if path.exists() or return_nonexistent:
            result = str(path)
        else:
            result = None
    # if result is None or not os.path.isfile(result):
    #    result = server.absolute_filename("/playgroundstatic/" + re.sub(r'[^A-Za-z0-9\-\_\.]', '', the_file)).path
    return result


def package_question_filename(the_file, return_nonexistent=False):
    parts = the_file.split(":")
    if len(parts) == 2:
        if not re.match(r'^data/questions/', parts[1]):
            parts[1] = 'data/questions/' + parts[1]
        if filename_invalid(parts[1]) or package_name_invalid(parts[0]):
            raise DAInvalidFilename("Invalid filename")
        try:
            path = Path(importlib.resources.files(parts[0]), parts[1])
        except:
            return None
        if path.exists() or return_nonexistent:
            return str(path)
    return None

# def default_absolute_filename(the_file):
#     return the_file

# absolute_filename = default_absolute_filename

# def set_absolute_filename(func):
#     # logmessage("Running set_absolute_filename in util")
#     global absolute_filename
#     absolute_filename = func


def nodoublequote(text):
    return re.sub(r'"', '', str(text))


def list_same(a, b):
    for elem in a:
        if elem not in b:
            return False
    for elem in b:
        if elem not in a:
            return False
    return True


def list_list_same(a, b):
    if len(a) != len(b):
        return False
    for i, a_item in enumerate(a):
        if len(a_item) != len(b[i]):
            return False
        for j, a_subitem in enumerate(a_item):
            if a_subitem != b[i][j]:
                return False
    return True


def process_action():
    """Process any pending interview action.

    Checks whether an action has been requested (e.g., via a URL created by
    :func:`url_action`) and, if so, handles it by calling :func:`force_ask`
    on the indicated variable.  If no action is pending, returns without
    doing anything.  This function is normally called automatically by
    docassemble before evaluating ``initial`` and ``mandatory`` blocks, but
    you can call it explicitly to control when actions are processed.
    """
    # logmessage("process_action() started")
    # logmessage("process_action: starting")
    if 'action' not in this_thread.current_info:
        to_be_gathered = [({'var': variable_dict, 'context': {}} if isinstance(variable_dict, str) else variable_dict) for variable_dict in this_thread.internal['gather']]  # change this later
        for variable_dict in to_be_gathered:
            # logmessage("process_action: considering a gather of " + variable_name)
            if defined(variable_dict['var']):
                if variable_dict in this_thread.internal['gather']:  # change this later
                    this_thread.internal['gather'].remove(variable_dict)
                elif variable_dict['var'] in this_thread.internal['gather']:  # change this later
                    this_thread.internal['gather'].remove(variable_dict['var'])  # change this later
            else:
                # logmessage("process_action: doing a gather of " + variable_name)
                if len(variable_dict['context']) > 0:
                    the_user_dict = get_user_dict()
                    for var_name, var_val in variable_dict['context'].items():
                        the_user_dict[var_name] = var_val
                    del the_user_dict
                force_ask_nameerror(variable_dict['var'])
        if 'event_stack' in this_thread.internal and this_thread.current_info['user']['session_uid'] in this_thread.internal['event_stack']:
            if len(this_thread.internal['event_stack'][this_thread.current_info['user']['session_uid']]) > 0:
                # if this_thread.interview_status.checkin:
                #     event_info = this_thread.internal['event_stack'][this_thread.current_info['user']['session_uid']].pop(0)
                # else:
                event_info = this_thread.internal['event_stack'][this_thread.current_info['user']['session_uid']][0]
                # logmessage("process_action: adding " + event_info['action'] + " to current_info")
                this_thread.current_info.update(event_info)
                the_context = event_info.get('context', {})
                if len(the_context) > 0:
                    the_user_dict = get_user_dict()
                    for var_name, var_val in the_context.items():
                        the_user_dict[var_name] = var_val
                    del the_user_dict
                if event_info['action'].startswith('_da_'):
                    # logmessage("process_action: forcing a re-run")
                    raise ForcedReRun()
                # logmessage("process_action: forcing a nameerror")
                this_thread.misc['forgive_missing_question'] = [event_info['action']]  # restore
                force_ask(event_info['action'])
                # logmessage("process_action: done with trying")
        # logmessage("process_action: returning")
        if 'forgive_missing_question' in this_thread.misc:
            del this_thread.misc['forgive_missing_question']
        return
    # logmessage("process_action() continuing")
    the_action = this_thread.current_info['action']
    # logmessage("process_action: action is " + repr(the_action))
    del this_thread.current_info['action']
    # if the_action == '_da_follow_up' and 'action' in this_thread.current_info['arguments']:
    #    this_thread.misc['forgive_missing_question'] = True
    #    # logmessage("Asking for " + this_thread.current_info['arguments']['action'])
    #    the_action = this_thread.current_info['arguments']['action']
    if the_action == '_da_priority_action' and '_action' in this_thread.current_info['arguments']:
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack']:
            this_thread.internal['event_stack'][unique_id] = []
        the_action = this_thread.current_info['arguments']['_action']
        if '_arguments' in this_thread.current_info['arguments']:
            this_thread.current_info['arguments'] = this_thread.current_info['arguments']['_arguments']
        else:
            this_thread.current_info['arguments'] = {}
    if the_action == '_da_force_ask' and 'variables' in this_thread.current_info['arguments']:
        this_thread.misc['forgive_missing_question'] = this_thread.current_info['arguments']['variables']  # restore
        force_ask(*this_thread.current_info['arguments']['variables'])
    if the_action == '_da_compute' and 'variables' in this_thread.current_info['arguments']:
        for variable_name in this_thread.current_info['arguments']['variables']:
            if variable_name not in [(variable_dict if isinstance(variable_dict, str) else variable_dict['var']) for variable_dict in this_thread.internal['gather']]:
                the_context = {}
                the_user_dict = get_user_dict()
                for var_name in ('x', 'i', 'j', 'k', 'l', 'm', 'n'):
                    if var_name in the_user_dict:
                        the_context[var_name] = the_user_dict[var_name]
                del the_user_dict
                this_thread.internal['gather'].append({'var': variable_name, 'context': the_context})
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack'] and len(this_thread.internal['event_stack'][unique_id]) and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and list_same(this_thread.internal['event_stack'][unique_id][0]['arguments']['variables'], this_thread.current_info['arguments']['variables']):
            # logmessage("popped the da_compute")
            this_thread.internal['event_stack'][unique_id].pop(0)
        # logmessage("forcing nameerror on " + this_thread.current_info['arguments']['variables'][0])
        force_ask_nameerror(this_thread.current_info['arguments']['variables'][0])
    if the_action == '_da_define' and 'variables' in this_thread.current_info['arguments']:
        for variable_name in this_thread.current_info['arguments']['variables']:
            if variable_name not in [(variable_dict if isinstance(variable_dict, str) else variable_dict['var']) for variable_dict in this_thread.internal['gather']]:
                the_context = {}
                the_user_dict = get_user_dict()
                for var_name in ('x', 'i', 'j', 'k', 'l', 'm', 'n'):
                    if var_name in the_user_dict:
                        the_context[var_name] = the_user_dict[var_name]
                del the_user_dict
                this_thread.internal['gather'].append({'var': variable_name, 'context': the_context})
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack'] and len(this_thread.internal['event_stack'][unique_id]) and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and list_same(this_thread.internal['event_stack'][unique_id][0]['arguments']['variables'], this_thread.current_info['arguments']['variables']):
            # logmessage("popped the da_compute")
            this_thread.internal['event_stack'][unique_id].pop(0)
        raise ForcedReRun()
    if the_action == '_da_set':
        for the_args in this_thread.current_info['arguments']['variables']:
            # logmessage("defining " + repr(the_args))
            define(*the_args)
            # logmessage("done defining " + repr(the_args))
        unique_id = this_thread.current_info['user']['session_uid']
        # logmessage("It is " + repr(this_thread.internal['event_stack'][unique_id][0]))
        # logmessage("The other is " + repr(this_thread.current_info['arguments']['variables']))
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack'] and len(this_thread.internal['event_stack'][unique_id]) and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and list_list_same(this_thread.internal['event_stack'][unique_id][0]['arguments']['variables'], this_thread.current_info['arguments']['variables']):
            # logmessage("popped the da_set")
            this_thread.internal['event_stack'][unique_id].pop(0)
        # logmessage("Doing ForcedReRun")
        raise ForcedReRun()
    if the_action == '_da_undefine':
        for undef_var in this_thread.current_info['arguments']['variables']:
            undefine(undef_var)
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack'] and len(this_thread.internal['event_stack'][unique_id]) and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and list_same(this_thread.internal['event_stack'][unique_id][0]['arguments']['variables'], this_thread.current_info['arguments']['variables']):
            # logmessage("popped the da_undefine")
            this_thread.internal['event_stack'][unique_id].pop(0)
        raise ForcedReRun()
    if the_action == '_da_invalidate':
        for undef_var in this_thread.current_info['arguments']['variables']:
            undefine(undef_var, invalidate=True)
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack'] and len(this_thread.internal['event_stack'][unique_id]) and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and list_same(this_thread.internal['event_stack'][unique_id][0]['arguments']['variables'], this_thread.current_info['arguments']['variables']):
            this_thread.internal['event_stack'][unique_id].pop(0)
        raise ForcedReRun()
    if the_action == '_da_list_remove':
        if 'action_item' in this_thread.current_info and 'action_list' in this_thread.current_info:
            try:
                this_thread.current_info['action_list'].pop(this_thread.current_info['action_item'])
                if len(this_thread.current_info['action_list'].elements) == 0 and hasattr(this_thread.current_info['action_list'], 'there_are_any'):
                    this_thread.current_info['action_list'].there_are_any = False
                if hasattr(this_thread.current_info['action_list'], 'there_is_another') and this_thread.current_info['action_list'].there_is_another:
                    del this_thread.current_info['action_list'].there_is_another
                if hasattr(this_thread.current_info['action_list'], '_necessary_length'):
                    del this_thread.current_info['action_list']._necessary_length
                if hasattr(this_thread.current_info['action_list'], 'ask_number') and this_thread.current_info['action_list'].ask_number and hasattr(this_thread.current_info['action_list'], 'target_number') and int(this_thread.current_info['action_list'].target_number) > 0:
                    this_thread.current_info['action_list'].target_number = int(this_thread.current_info['action_list'].target_number) - 1
            except BaseException as err:
                logmessage("process_action: _da_list_remove error: " + str(err))
                try:
                    logmessage("process_action: list is: " + str(this_thread.current_info['action_list'].instanceName))
                except:
                    pass
                try:
                    logmessage("process_action: item is: " + str(this_thread.current_info['action_item'].instanceName))
                except:
                    pass
        force_ask({'action': '_da_list_ensure_complete', 'arguments': {'group': this_thread.current_info['action_list'].instanceName}})
        # raise ForcedReRun()
    if the_action == '_da_dict_remove':
        if 'action_item' in this_thread.current_info and 'action_dict' in this_thread.current_info:
            try:
                this_thread.current_info['action_dict'].pop(this_thread.current_info['action_item'])
                if len(this_thread.current_info['action_dict'].elements) == 0 and hasattr(this_thread.current_info['action_dict'], 'there_are_any'):
                    this_thread.current_info['action_dict'].there_are_any = False
                if hasattr(this_thread.current_info['action_dict'], 'there_is_another') and this_thread.current_info['action_dict'].there_is_another:
                    del this_thread.current_info['action_dict'].there_is_another
                if len(this_thread.current_info['action_dict'].elements) == 0 and hasattr(this_thread.current_info['action_dict'], 'there_are_any'):
                    this_thread.current_info['action_dict'].there_are_any = False
                if hasattr(this_thread.current_info['action_dict'], 'ask_number') and this_thread.current_info['action_dict'].ask_number and hasattr(this_thread.current_info['action_dict'], 'target_number') and int(this_thread.current_info['action_dict'].target_number) > 0:
                    this_thread.current_info['action_dict'].target_number = int(this_thread.current_info['action_dict'].target_number) - 1
            except BaseException as err:
                logmessage("process_action: _da_dict_remove error: " + str(err))
                try:
                    logmessage("process_action: dict is: " + str(this_thread.current_info['action_dict'].instanceName))
                except:
                    pass
                try:
                    logmessage("process_action: item is: " + str(this_thread.current_info['action_item'].instanceName))
                except:
                    pass
        force_ask({'action': '_da_dict_ensure_complete', 'arguments': {'group': this_thread.current_info['action_dict'].instanceName}})
        # raise ForcedReRun()
    if the_action in ('_da_dict_edit', '_da_list_edit') and 'items' in this_thread.current_info['arguments']:
        if isinstance(this_thread.current_info['arguments']['items'][0], dict) and 'follow up' in this_thread.current_info['arguments']['items'][0] and isinstance(this_thread.current_info['arguments']['items'][0]['follow up'], list) and len(this_thread.current_info['arguments']['items'][0]['follow up']) > 0:
            this_thread.misc['forgive_missing_question'] = this_thread.current_info['arguments']['items'][0]['follow up']
        force_ask(*this_thread.current_info['arguments']['items'])
    if the_action in ('_da_list_ensure_complete', '_da_dict_ensure_complete') and 'group' in this_thread.current_info['arguments']:
        # logmessage("the_action is " + the_action)
        group_name = this_thread.current_info['arguments']['group']
        if illegal_variable_name(group_name):
            raise DAError("Illegal variable name")
        value(group_name).gathered_and_complete()
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack'] and len(this_thread.internal['event_stack'][unique_id]) and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and this_thread.internal['event_stack'][unique_id][0]['arguments']['group'] == group_name:
            this_thread.internal['event_stack'][unique_id].pop(0)
        raise ForcedReRun()
    if the_action == '_da_list_complete' and 'action_list' in this_thread.current_info:
        the_list = this_thread.current_info['action_list']
        # the_list._validate(the_list.object_type, the_list.complete_attribute)
        the_list.gathered_and_complete()
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack'] and len(this_thread.internal['event_stack'][unique_id]) and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and this_thread.internal['event_stack'][unique_id][0]['arguments']['list'] == the_list.instanceName:
            this_thread.internal['event_stack'][unique_id].pop(0)
        raise ForcedReRun()
    if the_action == '_da_dict_complete' and 'action_dict' in this_thread.current_info:
        # logmessage("_da_dict_complete")
        the_dict = this_thread.current_info['action_dict']
        the_dict.gathered_and_complete()
        # the_dict._validate(the_dict.object_type, the_dict.complete_attribute)
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' in this_thread.internal and unique_id in this_thread.internal['event_stack'] and len(this_thread.internal['event_stack'][unique_id]) and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and this_thread.internal['event_stack'][unique_id][0]['arguments']['dict'] == the_dict.instanceName:
            this_thread.internal['event_stack'][unique_id].pop(0)
        raise ForcedReRun()
    if the_action == '_da_list_add' and 'action_list' in this_thread.current_info:
        need_item = False
        the_list = this_thread.current_info['action_list']
        do_complete = this_thread.current_info['arguments'].get('complete', True)
        if hasattr(the_list, 'gathered') and the_list.gathered:
            the_list.was_gathered = True
            the_list.reset_gathered()
            if not the_list.auto_gather:
                if the_list.ask_object_type:
                    the_list.append(None)
                else:
                    if the_list.object_type is None:
                        need_item = True
                        unique_id = this_thread.current_info['user']['session_uid']
                        if 'event_stack' not in this_thread.internal:
                            this_thread.internal['event_stack'] = {}
                        if unique_id not in this_thread.internal['event_stack']:
                            this_thread.internal['event_stack'][unique_id] = []
                        item_action = {'action': the_list.item_name(len(the_list.elements)), 'arguments': {}}
                        this_thread.internal['event_stack'][unique_id].insert(0, item_action)
                        this_thread.current_info.update(item_action)
                    else:
                        the_list.appendObject()
        else:
            the_list.was_gathered = False
        if the_list.auto_gather:
            if the_list.ask_number:
                if hasattr(the_list, 'target_number'):
                    the_list.target_number = int(the_list.target_number) + 1
            else:
                if the_list.was_gathered:
                    the_list.there_is_another = False
                    if len(the_list.elements) > 0:
                        the_list.there_is_one_other = True
                else:
                    the_list.there_is_another = True
        if the_list.auto_gather and not the_list.ask_number:
            the_list.there_are_any = True
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' not in this_thread.internal:
            this_thread.internal['event_stack'] = {}
        if unique_id not in this_thread.internal['event_stack']:
            this_thread.internal['event_stack'][unique_id] = []
        if len(this_thread.internal['event_stack'][unique_id]) > 0 and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and this_thread.internal['event_stack'][unique_id][0]['arguments']['list'] == the_list.instanceName:
            this_thread.internal['event_stack'][unique_id].pop(0)
        if do_complete:
            the_action = {'action': '_da_list_complete', 'arguments': {'list': the_list.instanceName}}
            if need_item:
                this_thread.internal['event_stack'][unique_id].insert(1, the_action)
            else:
                this_thread.internal['event_stack'][unique_id].insert(0, the_action)
                this_thread.current_info.update(the_action)
        raise ForcedReRun()
        # the_list._validate(the_list.object_type, the_list.complete_attribute)
    if the_action == '_da_dict_add' and 'action_dict' in this_thread.current_info:
        # logmessage("_da_dict_add")
        the_dict = this_thread.current_info['action_dict']
        if hasattr(the_dict, 'gathered') and the_dict.gathered:
            if not the_dict.auto_gather:
                if hasattr(the_dict, 'new_item_name') and the_dict.new_item_name in the_dict.elements:
                    delattr(the_dict, 'new_item_name')
                else:
                    the_dict[the_dict.new_item_name]  # pylint: disable=pointless-statement
            the_dict.reset_gathered()
            if the_dict.auto_gather:
                if the_dict.ask_number:
                    the_dict.target_number = len(the_dict.elements) + 1
                else:
                    the_dict.there_is_another = False
                    the_dict.there_is_one_other = True
        if the_dict.auto_gather and not the_dict.ask_number:
            the_dict.there_are_any = True
        unique_id = this_thread.current_info['user']['session_uid']
        if 'event_stack' not in this_thread.internal:
            this_thread.internal['event_stack'] = {}
        if unique_id not in this_thread.internal['event_stack']:
            this_thread.internal['event_stack'][unique_id] = []
        if len(this_thread.internal['event_stack'][unique_id]) > 0 and this_thread.internal['event_stack'][unique_id][0]['action'] == the_action and this_thread.internal['event_stack'][unique_id][0]['arguments']['dict'] == the_dict.instanceName:
            this_thread.internal['event_stack'][unique_id].pop(0)
        the_action = {'action': '_da_dict_complete', 'arguments': {'dict': the_dict.instanceName}}
        this_thread.internal['event_stack'][unique_id].insert(0, the_action)
        this_thread.current_info.update(the_action)
        raise ForcedReRun()
    if the_action == '_da_exit':
        command('interview_exit')
    if the_action == 'need':
        for key in ['variable', 'variables']:
            if key in this_thread.current_info['arguments']:
                if isinstance(this_thread.current_info['arguments'][key], list):
                    for var in this_thread.current_info['arguments'][key]:
                        if var not in [(variable_dict if isinstance(variable_dict, str) else variable_dict['var']) for variable_dict in this_thread.internal['gather']]:
                            the_context = {}
                            the_user_dict = get_user_dict()
                            for var_name in ('x', 'i', 'j', 'k', 'l', 'm', 'n'):
                                if var_name in the_user_dict:
                                    the_context[var_name] = the_user_dict[var_name]
                            del the_user_dict
                            this_thread.internal['gather'].append({'var': var, 'context': the_context})
                elif this_thread.current_info['arguments'][key] not in [(variable_dict if isinstance(variable_dict, str) else variable_dict['var']) for variable_dict in this_thread.internal['gather']]:
                    the_context = {}
                    the_user_dict = get_user_dict()
                    for var_name in ('x', 'i', 'j', 'k', 'l', 'm', 'n'):
                        if var_name in the_user_dict:
                            the_context[var_name] = the_user_dict[var_name]
                    del the_user_dict
                    this_thread.internal['gather'].append({'var': this_thread.current_info['arguments'][key], 'context': the_context})
                del this_thread.current_info['arguments'][key]
        to_be_gathered = [({'var': variable_dict, 'context': {}} if isinstance(variable_dict, str) else variable_dict) for variable_dict in this_thread.internal['gather']]
        for variable_dict in to_be_gathered:
            if defined(variable_dict['var']):
                if variable_dict in this_thread.internal['gather']:  # change this later
                    this_thread.internal['gather'].remove(variable_dict)
                elif variable_dict['var'] in this_thread.internal['gather']:  # change this later
                    this_thread.internal['gather'].remove(variable_dict['var'])  # change this later
            else:
                # logmessage("process_action: doing a gather2: " + variable_name)
                force_ask_nameerror(variable_dict)
        if 'forgive_missing_question' in this_thread.misc:
            del this_thread.misc['forgive_missing_question']
        return
    # logmessage("process_action: calling force_ask")
    this_thread.misc['forgive_missing_question'] = [the_action]  # restore
    force_ask(the_action)


def url_action(action, **kwargs):
    """Return a URL that triggers an action in the current interview.

    When visited, the URL causes :func:`process_action` to run the specified
    action.  The action can run a code block labeled with ``event``, ask a
    question, or define a variable.

    Args:
        action (str): The name of the action (variable or event) to trigger.
        **kwargs: Arguments to pass to the action.  The special keyword
            argument ``_forget_prior`` (bool), if ``True``, discards any
            currently pending actions before running this one.

    Returns:
        str: A URL string that triggers the action when visited.
    """
    if contains_volatile.search(action):
        raise DAError("url_action cannot be used with a generic object or a variable iterator")
    if '_forget_prior' in kwargs:
        is_priority = bool(kwargs['_forget_prior'])
        del kwargs['_forget_prior']
        if is_priority:
            kwargs = {'_action': action, '_arguments': kwargs}
            action = '_da_priority_action'
    return url_of('flex_interview', action=myb64quote(json.dumps({'action': action, 'arguments': kwargs})), i=this_thread.current_info['yaml_filename'])


def myb64quote(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf-8'), 'base64').decode())


def myb64unquote(text):
    return codecs.decode(repad_byte(bytearray(text, encoding='utf-8')), 'base64').decode('utf-8')

# def set_debug_status(new_value):
#     global debug
#     debug = new_value


def debug_status():
    return server.debug
# grep -E -R -o -h "word\(['\"][^\)]+\)" * | sed "s/^[^'\"]+['\"]//g"


def action_menu_item(label, action, **kwargs):
    """Return a menu item dictionary that triggers an action when clicked.

    Constructs a dictionary with a ``label`` and a ``url`` (created via
    :func:`url_action`) for use in the ``menu_items`` special variable.

    Args:
        label (str): The text displayed in the menu.
        action (str): The action name to trigger when the item is clicked.
        **kwargs: Arguments passed on to the action via :func:`url_action`.
            The special argument ``_screen_size`` (``'small'`` or
            ``'large'``) restricts the item to the given screen size.

    Returns:
        dict: A dictionary with keys ``label`` and ``url``, and optionally
            ``screen_size``.
    """
    args = copy.deepcopy(kwargs)
    if '_screen_size' in args:
        del args['_screen_size']
        return {'label': label, 'url': url_action(action, **args), 'screen_size': kwargs['_screen_size']}
    return {'label': label, 'url': url_action(action, **args)}


def from_b64_json(string):
    """Decode a base-64 string and parse it as JSON, returning the resulting object.

    This is an advanced function used to integrate external systems with
    docassemble by decoding data that was encoded with base-64 JSON encoding.

    Args:
        string (str): A base-64-encoded JSON string, or ``None``.

    Returns:
        The Python object represented by the decoded JSON, or ``None`` if
            ``string`` is ``None``.
    """
    if string is None:
        return None
    return json.loads(base64.b64decode(repad(string)))


def repad(text):
    return text + ('=' * ((4 - len(text) % 4) % 4))


def repad_byte(text):
    return text + (equals_byte * ((4 - len(text) % 4) % 4))


class lister(ast.NodeVisitor):

    def __init__(self):
        self.stack = []

    def visit_Name(self, node):
        self.stack.append(['name', node.id])
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Attribute(self, node):
        self.stack.append(['attr', node.attr])
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Subscript(self, node):
        self.stack.append(['index', re.sub(r'\n', '', astunparse.unparse(node.slice))])
        ast.NodeVisitor.generic_visit(self, node)
    # def visit_BinOp(self, node):
    #     self.stack.append(['binop', re.sub(r'\n', '', astunparse.unparse(node))])
    #     ast.NodeVisitor.generic_visit(self, node)
    # def visit_Constant(self, node):
    #     return


def components_of(full_variable):
    node = ast.parse(full_variable, mode='eval')
    crawler = lister()
    crawler.visit(node)
    components = list(reversed(crawler.stack))
    start_index = 0
    for the_index, elem in enumerate(components):
        if elem[0] == 'name':
            start_index = the_index
    return components[start_index:]


def get_user_dict():
    frame = sys._getframe(1)
    while frame is not None:
        f_locals = frame.f_locals
        if 'user_dict' in f_locals:
            user_dict = f_locals['user_dict']
            if isinstance(user_dict, dict) and '_internal' in user_dict:
                return user_dict
        if '_internal' in f_locals:
            return f_locals
        frame = frame.f_back
    return {}

def invalidate(*pargs):
    """Make one or more variables undefined while remembering their prior values as defaults.

    Like :func:`undefine`, but also stores the current value so that it is
    offered as a default when the question is re-asked.

    Args:
        *pargs: Variable name strings to invalidate.
    """
    undefine(*pargs, invalidate=True)


def _undefine_internal_old(*pargs, invalidate=False):  # pylint: disable=redefined-outer-name
    vars_to_delete = []
    the_pargs = unpack_pargs(pargs)
    for var in the_pargs:
        str(var)
        if not isinstance(var, str):
            raise DAError("undefine() must be given a string, not " + repr(var) + ", a " + str(var.__class__.__name__))
        try:
            eval(var, {})
            continue
        except:
            vars_to_delete.append(var)
        components = components_of(var)
        if len(components) == 0 or len(components[0]) < 2:
            raise DAError("undefine: variable " + repr(var) + " is not a valid variable name")
    if len(vars_to_delete) == 0:
        return
    frame = sys._getframe(1)
    the_user_dict = frame.f_locals
    while '_internal' not in the_user_dict:
        frame = frame.f_back
        if frame is None:
            return
        if 'user_dict' in frame.f_locals:
            the_user_dict = frame.f_locals['user_dict']
            if '_internal' in the_user_dict:
                break
            return
        the_user_dict = frame.f_locals
    this_thread.probing = True
    if invalidate:
        for var in vars_to_delete:
            try:
                exec("_internal['dirty'][" + repr(var) + "] = " + var, the_user_dict)
            except:
                pass
    for var in vars_to_delete:
        try:
            exec('del ' + var, the_user_dict)
        except:
            pass
    this_thread.probing = False


def _undefine_internal_new(*pargs, invalidate=False):  # pylint: disable=redefined-outer-name
    vars_to_delete = []
    the_pargs = unpack_pargs(pargs)
    for var in the_pargs:
        str(var)
        if not isinstance(var, str):
            raise DAError("undefine() must be given a string, not " + repr(var) + ", a " + str(var.__class__.__name__))
        try:
            eval(var, {})
            continue
        except:
            vars_to_delete.append(var)
        components = components_of(var)
        if len(components) == 0 or len(components[0]) < 2:
            raise DAError("undefine: variable " + repr(var) + " is not a valid variable name")
    if len(vars_to_delete) == 0:
        return
    frame = sys._getframe(1)
    the_user_dict = frame.f_locals
    the_user_dict_g = frame.f_globals
    while '_internal' not in the_user_dict:
        frame = frame.f_back
        if frame is None:
            return
        if 'user_dict' in frame.f_locals:
            the_user_dict = frame.f_locals['user_dict']
            the_user_dict_g = frame.f_globals
            if '_internal' in the_user_dict:
                break
            return
        the_user_dict = frame.f_locals
        the_user_dict_g = frame.f_globals
    this_thread.probing = True
    if invalidate:
        for var in vars_to_delete:
            try:
                exec("_internal['dirty'][" + repr(var) + "] = " + var, the_user_dict_g, the_user_dict)
            except:
                pass
    for var in vars_to_delete:
        try:
            exec('del ' + var, the_user_dict_g, the_user_dict)
        except:
            pass
    this_thread.probing = False


if python313:
    _undefine_internal = _undefine_internal_new
else:
    _undefine_internal = _undefine_internal_old


def undefine(*pargs, invalidate=False):  # pylint: disable=redefined-outer-name
    """Delete one or more interview variables, making them undefined.

    If a variable is not defined, this function does nothing (no error is
    raised).  Multiple variable names can be passed at once.

    Args:
        *pargs: Variable name strings to undefine.
        invalidate (bool, optional): Internal flag; when ``True``, also
            saves the current value for use as a default. Use
            :func:`invalidate` instead of setting this directly. Defaults
            to ``False``.
    """
    _undefine_internal(*pargs, invalidate=invalidate)


def dispatch(var):
    """Present a nested menu driven by the value of a variable.

    Repeatedly evaluates the variable named by ``var``.  When the variable
    is set to the name of another variable, that variable is evaluated and
    then undefined, allowing the user to visit sub-menus or pages.  The
    loop ends when the variable is set to ``None``.

    Args:
        var (str): The name of the variable that controls the menu
            selection.

    Returns:
        bool: Always ``True``.
    """
    if not isinstance(var, str):
        raise DAError("dispatch() must be given a string")
    if illegal_variable_name(var):
        raise DAError("Illegal variable name")
    while value(var) != 'None':
        value(value(var))
        undefine(value(var))
        undefine(var)
    undefine(var)
    return True


def set_variables(variables, process_objects=False):
    """Update the current interview answers using a dictionary of variable names and values.

    Similar to calling :func:`define` repeatedly, but accepts a dictionary.

    Args:
        variables (dict): A dictionary mapping variable name strings to
            their new values.
        process_objects (bool, optional): If ``True``, converts the
            dictionary from docassemble's serializable object representation
            (e.g., from ``.as_serializable()``) into actual Python objects.
            Defaults to ``False``.
    """
    if hasattr(variables, 'instanceName') and hasattr(variables, 'elements'):
        variables = variables.elements
    if not isinstance(variables, dict):
        raise DAError("set_variables: argument must be a dictionary")
    user_dict = get_user_dict()
    if user_dict is None:
        raise DAError("set_variables: could not find interview answers")
    if process_objects:
        variables = server.transform_json_variables(variables)  # pylint: disable=assignment-from-none
    for var, val in variables.items():
        exec(var + " = None", user_dict)
        user_dict['__define_val'] = val
        exec(var + " = __define_val", user_dict)
        if '__define_val' in user_dict:
            del user_dict['__define_val']


def define(var, val):
    """Set an interview variable by name to the given value.

    Equivalent to writing ``var_name = val`` in a code block, but uses a
    string for the variable name.

    Args:
        var (str): The name of the variable to define (must be a valid
            Python identifier or expression).
        val: The value to assign to the variable.
    """
    ensure_definition(var, val)
    if not isinstance(var, str) or not re.search(r'^[A-Za-z_]', var):
        raise DAError("define() must be given a string as the variable name")
    user_dict = get_user_dict()
    if user_dict is None:
        raise DAError("define: could not find interview answers")
    # Trigger exceptions for the left hand side before creating __define_val
    exec(var + " = None", user_dict)
    # logmessage("Got past the lhs check")
    user_dict['__define_val'] = val
    exec(var + " = __define_val", user_dict)
    if '__define_val' in user_dict:
        del user_dict['__define_val']


class DefCaller(Enum):
    DEFINED = 1
    VALUE = 2
    SHOWIFDEF = 3

    def is_pure(self) -> bool:
        """The functions defined() and showifdef() don't affect the external state of the
            interview, and are idempotent, so they are pure functions"""
        return self in (self.DEFINED, self.SHOWIFDEF)

    def is_predicate(self) -> bool:
        """True if the function itself is a predicate (returns True/False)"""
        return self == self.DEFINED


def _defined_internal_with_prior(var, caller: DefCaller, alt=None):
    try:
        return _defined_internal(var, caller, alt=alt, prior=True)
    except:
        return _defined_internal(var, caller, alt=alt)


def _defined_internal_old(var, caller: DefCaller, alt=None, prior=False):
    """Checks if a variable is defined at all in the stack. Used by defined(),
    value(), and showifdef(). `var` is the name of the variable to check,
    `caller` is the name of the function calling (which determines what to do
    if the variable is found to be defined or not).

    if caller is:
    * DEFINED, then True/False is returned depending on if the variable is defined
    * VALUE, then the actual value of the variable is returned, after asking the
      user all of the questions necessary to answer it
    * SHOWIFDEF, then the value if returned, but only if no questions have to be asked
    """
    frame = sys._getframe(1)
    components = components_of(var)
    if len(components) == 0 or len(components[0]) < 2:
        raise DAError("defined: variable " + repr(var) + " is not a valid variable name")
    variable = components[0][1]
    the_user_dict = frame.f_locals
    failure_val = False if caller.is_predicate() else alt
    user_dict_name = 'old_user_dict' if prior else 'user_dict'
    while (variable not in the_user_dict) or prior:
        frame = frame.f_back
        if frame is None:
            if caller.is_pure():
                return failure_val
            force_ask_nameerror(variable)
        if user_dict_name in frame.f_locals:
            the_user_dict = frame.f_locals[user_dict_name]
            if variable in the_user_dict:
                break
            if caller.is_pure():
                return failure_val
            force_ask_nameerror(variable)
        else:
            the_user_dict = frame.f_locals
    if variable not in the_user_dict:
        if caller.is_pure():
            return failure_val
        force_ask_nameerror(variable)
    if len(components) == 1:
        if caller.is_predicate():
            return True
        return eval(variable, the_user_dict)
    cum_variable = ''
    if caller.is_pure():
        this_thread.probing = True
    has_random_instance_name = False
    for elem in components:
        if elem[0] == 'name':
            cum_variable = elem[1]
            continue
        if elem[0] == 'attr':
            base_var = cum_variable
            to_eval = "hasattr(" + cum_variable + ", " + repr(elem[1]) + ")"
            cum_variable += '.' + elem[1]
            try:
                result = eval(to_eval, the_user_dict)
            except:
                if caller.is_pure():
                    this_thread.probing = False
                    return failure_val
                force_ask_nameerror(base_var)
            if result:
                continue
            if caller.is_pure():
                this_thread.probing = False
                return failure_val
            the_cum = eval(base_var, the_user_dict)
            try:
                if not the_cum.has_nonrandom_instance_name:
                    has_random_instance_name = True
            except:
                pass
            if has_random_instance_name:
                force_ask_nameerror(cum_variable)
            getattr(the_cum, elem[1])
        elif elem[0] == 'index':
            try:
                the_index = eval(elem[1], the_user_dict)
            except:
                if caller.is_pure():
                    this_thread.probing = False
                    return failure_val
                value(elem[1])
            try:
                the_cum = eval(cum_variable, the_user_dict)
            except:
                if caller.is_pure():
                    this_thread.probing = False
                    return failure_val
                force_ask_nameerror(cum_variable)
            if hasattr(the_cum, 'instanceName') and hasattr(the_cum, 'elements'):
                var_elements = cum_variable + '.elements'
            else:
                var_elements = cum_variable
            if isinstance(the_index, int):
                to_eval = 'len(' + var_elements + ') > ' + str(the_index)
            else:
                to_eval = elem[1] + " in " + var_elements
            cum_variable += '[' + elem[1] + ']'
            try:
                result = eval(to_eval, the_user_dict)
            except:
                # the evaluation probably will never fail because we know the base variable is defined
                if caller.is_pure():
                    this_thread.probing = False
                    return failure_val
                force_ask_nameerror(cum_variable)
            if result:
                continue
            if caller.is_pure():
                this_thread.probing = False
                return failure_val
            try:
                if not the_cum.has_nonrandom_instance_name:
                    has_random_instance_name = True
            except:
                pass
            if has_random_instance_name:
                force_ask_nameerror(cum_variable)
            the_cum[the_index]  # pylint: disable=pointless-statement
    if caller.is_pure():
        this_thread.probing = False
    if caller.is_predicate():
        return True
    return eval(cum_variable, the_user_dict)


def _defined_internal_new(var, caller: DefCaller, alt=None, prior=False):
    """Checks if a variable is defined at all in the stack. Used by defined(),
    value(), and showifdef(). `var` is the name of the variable to check,
    `caller` is the name of the function calling (which determines what to do
    if the variable is found to be defined or not).

    if caller is:
    * DEFINED, then True/False is returned depending on if the variable is defined
    * VALUE, then the actual value of the variable is returned, after asking the
      user all of the questions necessary to answer it
    * SHOWIFDEF, then the value if returned, but only if no questions have to be asked
    """
    frame = sys._getframe(1)
    components = components_of(var)
    if len(components) == 0 or len(components[0]) < 2:
        raise DAError("defined: variable " + repr(var) + " is not a valid variable name")
    variable = components[0][1]
    the_user_dict = frame.f_locals
    the_user_dict_g = frame.f_globals
    failure_val = False if caller.is_predicate() else alt
    user_dict_name = 'old_user_dict' if prior else 'user_dict'
    while (variable not in the_user_dict) or prior:
        frame = frame.f_back
        if frame is None:
            if caller.is_pure():
                return failure_val
            force_ask_nameerror(variable)
        if user_dict_name in frame.f_locals:
            the_user_dict = frame.f_locals[user_dict_name]
            the_user_dict_g = frame.f_globals
            if variable in the_user_dict:
                break
            if caller.is_pure():
                return failure_val
            force_ask_nameerror(variable)
        else:
            the_user_dict = frame.f_locals
            the_user_dict_g = frame.f_globals
    if variable not in the_user_dict:
        if caller.is_pure():
            return failure_val
        force_ask_nameerror(variable)
    if len(components) == 1:
        if caller.is_predicate():
            return True
        return eval(variable, the_user_dict_g, the_user_dict)
    cum_variable = ''
    if caller.is_pure():
        this_thread.probing = True
    has_random_instance_name = False
    for elem in components:
        if elem[0] == 'name':
            cum_variable = elem[1]
            continue
        if elem[0] == 'attr':
            base_var = cum_variable
            to_eval = "hasattr(" + cum_variable + ", " + repr(elem[1]) + ")"
            cum_variable += '.' + elem[1]
            try:
                result = eval(to_eval, the_user_dict_g, the_user_dict)
            except:
                if caller.is_pure():
                    this_thread.probing = False
                    return failure_val
                force_ask_nameerror(base_var)
            if result:
                continue
            if caller.is_pure():
                this_thread.probing = False
                return failure_val
            the_cum = eval(base_var, the_user_dict_g, the_user_dict)
            try:
                if not the_cum.has_nonrandom_instance_name:
                    has_random_instance_name = True
            except:
                pass
            if has_random_instance_name:
                force_ask_nameerror(cum_variable)
            getattr(the_cum, elem[1])
        elif elem[0] == 'index':
            try:
                the_index = eval(elem[1], the_user_dict_g, the_user_dict)
            except:
                if caller.is_pure():
                    this_thread.probing = False
                    return failure_val
                value(elem[1])
            try:
                the_cum = eval(cum_variable, the_user_dict_g, the_user_dict)
            except:
                if caller.is_pure():
                    this_thread.probing = False
                    return failure_val
                force_ask_nameerror(cum_variable)
            if hasattr(the_cum, 'instanceName') and hasattr(the_cum, 'elements'):
                var_elements = cum_variable + '.elements'
            else:
                var_elements = cum_variable
            if isinstance(the_index, int):
                to_eval = 'len(' + var_elements + ') > ' + str(the_index)
            else:
                to_eval = elem[1] + " in " + var_elements
            cum_variable += '[' + elem[1] + ']'
            try:
                result = eval(to_eval, the_user_dict_g, the_user_dict)
            except:
                # the evaluation probably will never fail because we know the base variable is defined
                if caller.is_pure():
                    this_thread.probing = False
                    return failure_val
                force_ask_nameerror(cum_variable)
            if result:
                continue
            if caller.is_pure():
                this_thread.probing = False
                return failure_val
            try:
                if not the_cum.has_nonrandom_instance_name:
                    has_random_instance_name = True
            except:
                pass
            if has_random_instance_name:
                force_ask_nameerror(cum_variable)
            the_cum[the_index]  # pylint: disable=pointless-statement
    if caller.is_pure():
        this_thread.probing = False
    if caller.is_predicate():
        return True
    return eval(cum_variable, the_user_dict_g, the_user_dict)


if python313:
    _defined_internal = _defined_internal_new
else:
    _defined_internal = _defined_internal_old


def value(var: str, prior=False):
    """Return the value of an interview variable specified by name.

    Equivalent to evaluating the variable directly, but uses a string for
    the variable name.  If the variable is not yet defined, docassemble will
    ask questions to define it.

    Args:
        var (str): The name of the variable whose value to return.
        prior (bool, optional): If ``True``, on screens loaded after the
            user pressed the Back button, look in the previous set of
            interview answers. Defaults to ``False``.

    Returns:
        The value of the specified variable.
    """
    str(var)
    if not isinstance(var, str):
        raise DAError("value() must be given a string")
    try:
        return eval(var, {})
    except:
        pass
    if re.search(r'[\(\)\n\r]|lambda:|lambda ', var):
        raise DAError("value() is invalid: " + repr(var))
    if prior:
        return _defined_internal_with_prior(var, DefCaller.VALUE)
    return _defined_internal(var, DefCaller.VALUE)


def defined(var: str, prior=False) -> bool:
    """Return ``True`` if the named interview variable is already defined.

    Checks whether the variable is defined without triggering docassemble's
    question-asking process.  The variable name must be passed as a string.

    Args:
        var (str): The name of the variable to check.
        prior (bool, optional): If ``True``, on screens loaded after the
            user pressed the Back button, also check the previous set of
            interview answers. Defaults to ``False``.

    Returns:
        bool: ``True`` if the variable is defined, ``False`` otherwise.
    """
    str(var)
    if not isinstance(var, str):
        raise DAError("defined() must be given a string")
    if not re.search(r'[A-Za-z][A-Za-z0-9\_]*', var):
        raise DAError("defined() must be given a valid Python variable name")
    try:
        eval(var, {})
        return True
    except:
        pass
    if prior:
        return _defined_internal_with_prior(var, DefCaller.VALUE)
    return _defined_internal(var, DefCaller.DEFINED)


def showifdef(var: str, alternative='', prior=False):
    """Return the value of a variable if it is defined, otherwise return alternative text.

    Args:
        var (str): The name of the variable whose value to return.
        alternative (optional): The value to return when the variable is
            not defined. Defaults to ``''``.
        prior (bool, optional): If ``True``, on screens loaded after the
            user pressed the Back button, also check the previous set of
            interview answers. Defaults to ``False``.

    Returns:
        The value of the variable if it is defined, otherwise
            ``alternative``.
    """
    # A combination of the preambles of defined and value
    str(var)
    if not isinstance(var, str):
        raise DAError("showifdef() must be given a string")
    if not re.search(r'[A-Za-z][A-Za-z0-9\_]*', var):
        raise DAError("showifdef() must be given a valid Python variable name")
    try:
        return eval(var, {})
    except:
        pass
    if re.search(r'[\(\)\n\r]|lambda:|lambda ', var):
        raise DAError("showifdef() is invalid: " + repr(var))
    if prior:
        return _defined_internal_with_prior(var, DefCaller.SHOWIFDEF, alt=alternative)
    return _defined_internal(var, DefCaller.SHOWIFDEF, alt=alternative, prior=prior)


def illegal_variable_name(var):
    if re.search(r'[\n\r]', var):
        return True
    try:
        t = ast.parse(var)
    except:
        return True
    detector = docassemble.base.astparser.detectIllegal()
    detector.visit(t)
    return detector.illegal


def single_paragraph(text):
    """Replace all line breaks in the text with spaces, collapsing it to a single paragraph.

    Useful when embedding user-supplied text in a Markdown block-quote or
    similar context where internal line breaks would break the formatting.

    Args:
        text (str): The text to process.

    Returns:
        str: The text with all newline characters replaced by spaces.
    """
    return newlines.sub(' ', str(text))


def quote_paragraphs(text):
    """Wrap each paragraph in the text with Markdown block-quote formatting.

    Adds ``> `` before each paragraph so that the text is displayed as a
    Markdown block-quote.

    Args:
        text (str): The text to quote.

    Returns:
        str: The text with each paragraph prefixed by ``'> '``.
    """
    return '> ' + single_newline.sub('\n> ', str(text).strip())


def set_live_help_status(availability=None, mode=None, partner_roles=None):
    """Configure the live help (chat) feature for the current interview session.

    Args:
        availability (str or bool, optional): Set to ``'available'`` or
            ``True`` to enable live help, ``'unavailable'`` or ``False``
            to disable it, or ``'observeonly'`` to allow the monitor to
            observe but not chat.
        mode (str, optional): Chat mode; one of ``'help'``, ``'peer'``,
            or ``'peerhelp'``.
        partner_roles (str or list, optional): The roles of monitors with
            whom the user may chat.
    """
    if availability in ['available', True]:
        this_thread.internal['livehelp']['availability'] = 'available'
    if availability in ['unavailable', False]:
        this_thread.internal['livehelp']['availability'] = 'unavailable'
    if availability in ['observeonly']:
        this_thread.internal['livehelp']['availability'] = 'observeonly'
    if mode in ['help', 'peer', 'peerhelp']:
        this_thread.internal['livehelp']['mode'] = mode
    # if roles is not None:
    #     new_roles = set()
    #     for parg in roles:
    #         if type(parg) is list:
    #             plist = parg
    #         else:
    #             plist = [parg]
    #         for arg in plist:
    #             new_roles.add(arg)
    #     this_thread.internal['livehelp']['roles'] = list(new_roles)
    if partner_roles is not None:
        new_roles = set()
        if isinstance(partner_roles, str):
            partner_roles = [partner_roles]
        for parg in partner_roles:
            if isinstance(parg, list):
                plist = parg
            else:
                plist = [parg]
            for arg in plist:
                new_roles.add(arg)
        this_thread.internal['livehelp']['partner_roles'] = list(new_roles)
    if 'mode' in this_thread.internal['livehelp'] and this_thread.internal['livehelp']['mode'] in ['help', 'peerhelp'] and 'availability' in this_thread.internal['livehelp'] and this_thread.internal['livehelp']['availability'] == 'available' and ('partner_roles' not in this_thread.internal['livehelp'] or len(this_thread.internal['livehelp']['partner_roles']) == 0):
        logmessage("set_live_help_status: if no partner_roles are set, users cannot get help from any monitors")


def phone_number_in_e164(number, country=None):
    """Return a phone number formatted in E.164 international format.

    Args:
        number (str): The phone number to format.
        country (str, optional): An ISO 3166-1 alpha-2 country code (e.g.
            ``'US'``, ``'SE'``) used to interpret the number. Defaults to
            the result of :func:`get_country`.

    Returns:
        str or None: The number in E.164 format (e.g. ``'+12025551234'``),
            or ``None`` if the number could not be formatted.
    """
    ensure_definition(number, country)
    if country is None:
        country = get_country() or 'US'
    use_whatsapp = False
    if isinstance(number, str):
        m = re.search(r'^whatsapp:(.*)', number)
        if m:
            number = m.group(1)
            use_whatsapp = True
    try:
        pn = phonenumbers.parse(number, country)
        output = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
    except:
        return None
    if use_whatsapp:
        return 'whatsapp:' + output
    return output


def phone_number_is_valid(number, country=None):
    """Return ``True`` if the phone number is valid for the specified country.

    Args:
        number (str): The phone number to validate.
        country (str, optional): An ISO 3166-1 alpha-2 country code used
            to determine applicable standards. Defaults to the result of
            :func:`get_country`.

    Returns:
        bool: ``True`` if the number is valid, ``False`` otherwise.
    """
    ensure_definition(number, country)
    if country is None:
        country = get_country() or 'US'
    if isinstance(number, str):
        m = re.search(r'^whatsapp:(.*)', number)
        if m:
            number = m.group(1)
    try:
        pn = phonenumbers.parse(number, country)
    except:
        return False
    if phonenumbers.is_possible_number(pn) and phonenumbers.is_valid_number(pn):
        return True
    return False


def phone_number_part(number, part, country=None):
    """Return a specific segment of a phone number's national format.

    Splits the nationally formatted phone number on non-digit separators and
    returns the segment at the given zero-based index.

    Args:
        number (str): The phone number to parse.
        part (int): The zero-based index of the segment to return
            (e.g. ``0`` for area code, ``1`` for exchange, ``2`` for
            subscriber number).
        country (str, optional): An ISO 3166-1 alpha-2 country code used
            to format the number. Defaults to the result of
            :func:`get_country`.

    Returns:
        str: The requested segment, or an empty string if parsing fails or
            the index is out of range.
    """
    ensure_definition(number, part, country)
    if country is None:
        country = get_country() or 'US'
    if isinstance(number, str):
        m = re.search(r'^whatsapp:(.*)', number)
        if m:
            number = m.group(1)
    try:
        pn = phonenumbers.parse(number, country)
    except:
        return ''
    formatted_number = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)
    parts = [x for x in re.split(r'[^0-9]+', formatted_number) if re.search(r'[0-9]', x)]
    if part < len(parts):
        return parts[part]
    return ''


def phone_number_formatted(number, country=None):
    """Return a phone number in the national format for the specified country.

    Args:
        number (str): The phone number to format.
        country (str, optional): An ISO 3166-1 alpha-2 country code used
            to determine national formatting conventions. Defaults to the
            result of :func:`get_country`.

    Returns:
        str or None: The number in national format, or ``None`` if the
            number could not be formatted.
    """
    ensure_definition(number, country)
    if number.__class__.__name__ == 'DAEmpty':
        return str(number)
    if country is None:
        country = get_country() or 'US'
    if isinstance(number, str):
        m = re.search(r'^whatsapp:(.*)', number)
        if m:
            number = m.group(1)
    try:
        pn = phonenumbers.parse(number, country)
        output = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)
    except:
        return None
    return output


def dict_as_json(user_dict, include_internal=False):
    return json.dumps(serializable_dict(user_dict, include_internal=include_internal), sort_keys=True, indent=2)


def serializable_dict(user_dict, include_internal=False):
    result_dict = {}
    for key, data in user_dict.items():
        if key in ('_internal', 'nav') and not include_internal:
            continue
        if key == '__builtins__':
            continue
        if isinstance(data, (types.ModuleType, types.FunctionType, TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, FileType)):
            continue
        result_dict[key] = safe_json(data)
    return result_dict


def safe_json(the_object, level=0, is_key=False):
    if level > 20:
        return 'None' if is_key else None
    if isinstance(the_object, (str, bool, int, float)):
        return the_object
    if isinstance(the_object, list):
        return [safe_json(x, level=level+1) for x in the_object]
    if isinstance(the_object, dict):
        new_dict = {}
        used_string = False
        used_non_string = False
        for key, val in the_object.items():
            the_key = safe_json(key, level=level+1, is_key=True)
            if isinstance(the_key, str):
                used_string = True
            else:
                used_non_string = True
            new_dict[the_key] = safe_json(val, level=level+1)
        if used_non_string and used_string:
            corrected_dict = {}
            for key, val in new_dict.items():
                corrected_dict[str(key)] = val
            return corrected_dict
        return new_dict
    if isinstance(the_object, set):
        new_list = []
        for sub_object in the_object:
            new_list.append(safe_json(sub_object, level=level+1))
        return new_list
    if hasattr(the_object, "as_dict") and callable(the_object.as_dict):
        return the_object.as_dict()
    if hasattr(the_object, "to_json") and callable(the_object.to_json):
        return the_object.to_json()
    if isinstance(the_object, TypeType):
        the_class_name = class_name(the_object)
        if not the_class_name.startswith('docassemble.'):
            return 'None'
        return {'_class': 'type', 'name': the_class_name}
    if isinstance(the_object, (types.ModuleType, types.FunctionType, TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, FileType)):
        return 'None' if is_key else None
    if isinstance(the_object, (datetime.datetime, datetime.date, datetime.time)):
        return the_object.isoformat()
    if isinstance(the_object, decimal.Decimal):
        return float(the_object)
    if isinstance(the_object, DANav):
        return {'past': list(the_object.past), 'current': the_object.current, 'hidden': (the_object.hidden if hasattr(the_object, 'hidden') else False), 'progressive': (the_object.progressive if hasattr(the_object, 'progressive') else True)}
    from docassemble.base.util import DAObject  # pylint: disable=import-outside-toplevel
    if isinstance(the_object, DAObject):
        new_dict = {}
        new_dict['_class'] = type_name(the_object)
        if the_object.__class__.__name__ in ('DALazyTemplate', 'DALazyTableTemplate'):
            if hasattr(the_object, 'instanceName'):
                new_dict['instanceName'] = the_object.instanceName
            return new_dict
        for key, data in the_object.__dict__.items():
            if key in ['has_nonrandom_instance_name', 'attrList']:
                continue
            new_dict[safe_json(key, level=level+1, is_key=True)] = safe_json(data, level=level+1)
        return new_dict
    try:
        json.dumps(the_object)
    except:
        return 'None' if is_key else None
    return the_object


def referring_url(default=None, current=False):
    """Return the URL that the user was visiting when the interview session was created.

    Retrieves the HTTP Referer URL recorded when the session started.  If
    the URL is unavailable (e.g., the user typed the URL directly), returns
    the ``default`` value or the ``exitpage`` configuration setting.

    Args:
        default (optional): Value to return if the referring URL is not
            available. If ``None``, falls back to the ``exitpage``
            configuration setting. Defaults to ``None``.
        current (bool, optional): If ``True``, returns the Referer of the
            current request instead of the session-start Referer. Defaults
            to ``False``.

    Returns:
        str: The referring URL, the ``default`` value, or the ``exitpage``
            URL.
    """
    if current:
        url = server.get_referer()
    else:
        url = this_thread.internal.get('referer', None)
    if url is None:
        if default is None:
            default = server.daconfig.get('exitpage', 'https://docassemble.org')
        url = default
    return url


def type_name(the_object):
    name = str(type(the_object))
    m = re.search(r'\'(.*)\'', name)
    if m:
        return m.group(1)
    return name


def class_name(the_object):
    name = str(the_object)
    m = re.search(r'\'(.*)\'', name)
    if m:
        return m.group(1)
    return name


def plain(text, default=None):
    """Return the text as-is, or an empty string (or default) if the text is blank.

    Useful in templates when you want blank values to produce no output
    instead of an empty string.

    Args:
        text: The value to return.
        default (optional): Value to return if ``text`` is blank or
            ``None``. Defaults to ``None`` (returns ``''``).

    Returns:
        str: The text, or the default value if the text is empty.
    """
    ensure_definition(text, default)
    if text is None or str(text).strip() == '':
        if default is None:
            return ''
        return default
    return text


def bold(text, default=None):
    """Return the text wrapped in Markdown bold formatting, or an empty string if blank.

    If ``text`` is empty and ``default`` is provided, wraps ``default`` in
    bold formatting instead.

    Args:
        text: The value to make bold.
        default (optional): Fallback value (also bolded) if ``text`` is
            blank. Defaults to ``None`` (returns ``''``).

    Returns:
        str: The text wrapped in ``**...**`` Markdown, or ``''`` if blank
            and no default is given.
    """
    ensure_definition(text, default)
    if text is None or str(text).strip() == '':
        if default is None:
            return ''
        return '**' + str(default) + '**'
    return '**' + re.sub(r'\*', '', str(text)) + '**'


def italic(text, default=None):
    """Return the text wrapped in Markdown italic formatting, or an empty string if blank.

    If ``text`` is empty and ``default`` is provided, wraps ``default`` in
    italic formatting instead.

    Args:
        text: The value to make italic.
        default (optional): Fallback value (also italicized) if ``text``
            is blank. Defaults to ``None`` (returns ``''``).

    Returns:
        str: The text wrapped in ``_..._`` Markdown, or ``''`` if blank
            and no default is given.
    """
    ensure_definition(text, default)
    if text is None or str(text).strip() == '':
        if default is None:
            return ''
        return '_' + str(default) + '_'
    return '_' + re.sub(r'\_', '', str(text)) + '_'

# def inspector():
#     frame = inspect.stack()[1][0]
#     for key in frame.__dict__.keys():
#         logmessage(str(key))


def indent(text, by=None):
    """Indent each line of the text by a number of spaces.

    Useful when embedding a paragraph or table inside a Markdown bulleted
    list to keep the content associated with the list item.

    Args:
        text (str): The text to indent.
        by (int, optional): Number of spaces to add at the start of each
            line. Defaults to ``4``.

    Returns:
        str: The text with each line prefixed by the specified number of
            spaces.
    """
    ensure_definition(text, by)
    if by is None:
        by = 4
    text = " " * by + str(text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n', '\n' + (" " * by), text)
    return text


def yesno(the_value, invert=False):
    """Return ``'Yes'`` or ``'No'`` based on the truth value of the argument.

    Useful for populating PDF checkbox fields that expect ``'Yes'`` or
    ``'No'`` strings.

    Args:
        the_value: The value to evaluate.
        invert (bool, optional): If ``True``, returns ``'No'`` for truthy
            values and ``'Yes'`` for falsy values. Defaults to ``False``.

    Returns:
        str: ``'Yes'`` or ``'No'``, or ``''`` if the value is empty.
    """
    ensure_definition(the_value, invert)
    if the_value is None or the_value == '' or the_value.__class__.__name__ == 'DAEmpty':
        return ""
    if the_value:
        if invert:
            return "No"
        return 'Yes'
    if invert:
        return 'Yes'
    return "No"


def noyes(the_value, invert=False):
    """Return ``'No'`` or ``'Yes'`` based on the truth value of the argument.

    The inverse of :func:`yesno`: returns ``'No'`` for truthy values and
    ``'Yes'`` for falsy values.  Useful for populating PDF checkbox fields.

    Args:
        the_value: The value to evaluate.
        invert (bool, optional): If ``True``, reverses the output (same
            behavior as :func:`yesno`). Defaults to ``False``.

    Returns:
        str: ``'No'`` or ``'Yes'``, or ``''`` if the value is empty.
    """
    ensure_definition(the_value, invert)
    if the_value is None or the_value == '' or the_value.__class__.__name__ == 'DAEmpty':
        return ""
    if the_value:
        if invert:
            return 'Yes'
        return "No"
    if invert:
        return "No"
    return 'Yes'


def split(text, breaks, index):
    """Split text into character-length segments at word boundaries and return one segment.

    Useful for filling in PDF form fields when a single phrase must be
    distributed across multiple fields.  Splits on word breaks where possible.

    Args:
        text (str): The phrase to split.
        breaks (int or list): Maximum character length of each segment.
            A single integer splits into two parts; a list of integers
            splits into ``len(breaks) + 1`` parts.
        index (int or str): The zero-based index of the segment to return,
            or ``'all'`` to return a list of all segments.

    Returns:
        str or list: The requested segment string, ``''`` if the index is
            out of range, or a list of all segments when ``index='all'``.
    """
    ensure_definition(text, breaks, index)
    text = re.sub(r'[\n\r]+', "\n", str(text).strip())
    if not isinstance(breaks, list):
        breaks = [breaks]
    lastbreakpoint = 0
    newbreaks = []
    for the_breakpoint in breaks:
        newbreaks.append(the_breakpoint + lastbreakpoint)
        lastbreakpoint = the_breakpoint
    breaks = newbreaks
    if len(breaks) == 0:
        breaks = [0]
    elif breaks[0] != 0:
        breaks = [0] + breaks
    breaks = breaks + [float("inf")]
    parts = []
    current_index = 0
    last_space = 0
    last_break = 0
    text_length = len(text)
    i = 0
    while i < text_length:
        if text[i] == "\n":
            parts.append(text[last_break:i].strip())
            last_space = i
            last_break = i
            current_index += 1
            i += 1
            continue
        if text[i] == ' ':
            last_space = i
        if i > breaks[current_index + 1] - 1:
            if last_space <= last_break:
                parts.append(text[last_break:i].strip())
                last_break = i
                current_index += 1
            else:
                parts.append(text[last_break:last_space].strip())
                last_break = last_space
                i = last_space
                current_index += 1
        i += 1
    parts.append(text[last_break:].strip())
    if index == 'all':
        return parts
    if int(float(index)) < len(parts):
        return parts[int(float(index))]
    return ''


def showif(var, condition, alternative=''):
    """Return the value of a variable if a condition is true, otherwise return alternative text.

    The variable name is only evaluated when the condition is true, preventing
    unnecessary question-asking.

    Args:
        var (str): The name of the variable whose value to return.
        condition: A condition that is evaluated to decide whether to return
            the variable's value.
        alternative (optional): The value to return when the condition is
            false. Defaults to ``''``.

    Returns:
        The value of the variable if the condition is true, otherwise
            ``alternative``.
    """
    ensure_definition(var, condition, alternative)
    if condition:
        return value(var)
    return alternative


def log(the_message, priority='log'):
    """Log a message to the server log, the browser console, or the user's screen.

    Args:
        the_message (str): The message to log.
        priority (str, optional): Destination and style. Use ``'log'`` for
            the server log, ``'console'`` for the browser console,
            ``'javascript'`` to run the message as JavaScript, or a
            Bootstrap alert level (``'success'``, ``'info'``, ``'danger'``,
            etc.) to show a popup notification. Defaults to ``'log'``.
    """
    if priority == 'log':
        logmessage(str(the_message))
    else:
        this_thread.message_log.append({'message': str(the_message), 'priority': priority})


def get_message_log():
    try:
        return this_thread.message_log
    except:
        return []


def encode_name(var):
    """Return the base64-encoded form of a Python variable name.

    Used internally to represent variable names as HTML input element names.

    Args:
        var (str): The Python variable name to encode.

    Returns:
        str: The base64-encoded variable name (without padding ``=`` characters).
    """
    return re.sub(r'[\n=]', '', codecs.encode(var.encode('utf-8'), 'base64').decode())


def decode_name(var):
    """Return the plain-text Python variable name from a base64-encoded form.

    The inverse of :func:`encode_name`.

    Args:
        var (str): A base64-encoded variable name.

    Returns:
        str: The decoded Python variable name.
    """
    return codecs.decode(repad_byte(bytearray(var, encoding='utf-8')), 'base64').decode('utf-8')


def interview_list(exclude_invalid=True, action=None, filename=None, session=None, user_id=None, query=None, include_dict=True, delete_shared=False, next_id=None):
    """Return information about interview sessions, or perform bulk session operations.

    If the current user is logged in, returns a paginated list of interview
    session dictionaries. Can also delete sessions.

    Args:
        exclude_invalid (bool, optional): If ``True``, omit sessions where
            the interview could not be loaded or decrypted. Defaults to
            ``True``.
        action (str, optional): Pass ``'delete_all'`` to delete matching
            sessions (returns count deleted), or ``'delete'`` to delete a
            single session specified by ``filename`` and ``session``.
        filename (str, optional): Limit results to sessions of this
            interview filename.
        session (str, optional): Limit results to this session ID.
        user_id (int or str, optional): User ID to filter by, or ``'all'``
            for all users. Defaults to the current user.
        query: An optional query expression for complex filtering.
        include_dict (bool, optional): If ``True``, include the session
            dictionary in the results. Defaults to ``True``.
        delete_shared (bool, optional): When deleting, also delete shared
            sessions. Defaults to ``False``.
        next_id (str, optional): Pagination token from a previous call.

    Returns:
        tuple or int or None: A ``(list, next_id)`` tuple for listing, an
            integer when deleting, or ``None`` if the user is not logged in.
    """
    if this_thread.current_info['user']['is_authenticated']:
        if user_id == 'all' or session is not None:
            user_id = None
        elif user_id is None:
            user_id = this_thread.current_info['user']['the_user_id']
        elif not isinstance(user_id, int):
            raise DAError("interview_list: user_id must be integer or 'all'")
        if action not in (None, 'delete_all', 'delete'):
            raise DAError("interview_list: invalid action")
        if action == 'delete' and (filename is None or session is None):
            raise DAError("interview_list: a filename and session must be provided when delete is the action.")
        if action is None:
            if next_id is not None:
                try:
                    start_id = int(myb64unquote(next_id))
                    assert start_id >= 0
                except:
                    raise DAError("interview_list: invalid next_id.")
            else:
                start_id = None
            (the_list, start_id) = server.user_interviews(user_id=user_id, secret=this_thread.current_info['secret'], exclude_invalid=exclude_invalid, action=action, filename=filename, session=session, include_dict=include_dict, delete_shared=delete_shared, start_id=start_id, query=query)  # pylint: disable=assignment-from-none,unpacking-non-sequence
            if start_id is None:
                return (the_list, None)
            return (the_list, myb64quote(str(start_id)))
        return server.user_interviews(user_id=user_id, secret=this_thread.current_info['secret'], exclude_invalid=exclude_invalid, action=action, filename=filename, session=session, include_dict=include_dict, delete_shared=delete_shared, query=query)
    return None


def interview_menu(*pargs, **kwargs):
    """Return the list of available interviews shown at the ``/list`` page.

    Returns:
        list: A list of dictionaries, each describing an interview with
            keys such as ``title``, ``filename``, ``link``, ``tags``,
            and ``metadata``.
    """
    return server.interview_menu(*pargs, **kwargs)


def get_user_list(include_inactive=False, next_id=None):
    """Return a paginated list of registered users on the server.

    Requires ``admin``, ``advocate``, or the ``access_user_info`` permission.

    Args:
        include_inactive (bool, optional): If ``True``, include inactive
            users in the results. Defaults to ``False``.
        next_id (str, optional): Pagination token from a previous call.

    Returns:
        tuple or None: A ``(list, next_id)`` tuple where the list contains
            user-info dictionaries, or ``None`` if the user is not logged in.
    """
    if this_thread.current_info['user']['is_authenticated']:
        if next_id is not None:
            try:
                start_id = int(myb64unquote(next_id))
                assert start_id >= 0
            except:
                raise DAError("get_user_list: invalid next_id.")
        else:
            start_id = None
        (the_list, start_id) = server.get_user_list(include_inactive=include_inactive, start_id=start_id)  # pylint: disable=assignment-from-none,unpacking-non-sequence
        if start_id is None:
            return (the_list, None)
        return (the_list, myb64quote(str(start_id)))
    return None


def manage_privileges(*pargs):
    """List, add, remove, or inspect privilege types on the system.

    Requires ``admin`` privileges or a custom privilege with the appropriate
    permissions.

    Args:
        *pargs: The first argument is the command (``'list'``, ``'add'``,
            ``'remove'``, or ``'inspect'``).  ``'add'`` and ``'remove'``
            take one or more privilege name strings as additional arguments.
            ``'inspect'`` takes a single privilege name.

    Returns:
        list or bool or None: The list of privileges for ``'list'``,
            permission details for ``'inspect'``, ``True`` for successful
            ``'add'``/``'remove'``, or ``None`` if not authenticated.
    """
    if this_thread.current_info['user']['is_authenticated']:
        arglist = list(pargs)
        if len(arglist) == 0:
            the_command = 'list'
        else:
            the_command = arglist.pop(0)
        if the_command == 'list':
            return server.get_privileges_list()
        if the_command == 'inspect':
            if len(arglist) != 1:
                raise DAError("manage_privileges: invalid number of arguments")
            return server.get_permissions_of_privilege(arglist[0])
        if the_command == 'add':
            for priv in arglist:
                server.add_privilege(priv)
            if len(arglist) > 0:
                return True
        elif the_command == 'remove':
            for priv in arglist:
                server.remove_privilege(priv)
            if len(arglist) > 0:
                return True
        else:
            raise DAError("manage_privileges: invalid command")
    return None


def get_user_info(user_id=None, email=None):
    """Return profile information for a user.

    With no arguments, returns information about the currently logged-in
    user.  To look up another user, provide their ``user_id`` or ``email``.
    Requires the user to be logged in; admin/advocate or ``access_user_info``
    permission is required to look up other users.

    Args:
        user_id (int, optional): The user ID of the user to look up.
        email (str, optional): The e-mail address of the user to look up.

    Returns:
        dict or None: A dictionary of user profile information, or ``None``
            if no user is found.
    """
    if this_thread.current_info['user']['is_authenticated'] and user_id is None and email is None:
        user_id = this_thread.current_info['user']['the_user_id']
    return server.get_user_info(user_id=user_id, email=email)


def set_user_info(**kwargs):
    """Write information to a user's profile.

    Updates profile fields for the current user, or for another user when
    ``user_id`` or ``email`` is provided.  Accepted keyword parameters
    include ``first_name``, ``last_name``, ``country``, ``language``,
    ``organization``, ``timezone``, ``password``, ``active``,
    ``privileges``, and others.  Requires the user to be logged in.

    Args:
        **kwargs: Profile fields to update.  Use ``user_id`` or ``email``
            to target a specific user.
    """
    user_id = kwargs.get('user_id', None)
    email = kwargs.get('email', None)
    server.set_user_info(**kwargs)
    if 'privileges' in kwargs and isinstance(kwargs['privileges'], (list, tuple)) and len(kwargs['privileges']) > 0:
        this_thread.current_info['user']['roles'] = list(kwargs['privileges'])
    if (user_id is None and email is None) or (user_id is not None and user_id == this_thread.current_info['user']['theid']) or (email is not None and email == this_thread.current_info['user']['email']):
        for key, val in kwargs.items():
            if key in ('country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
                this_thread.current_info['user'][key] = val
            if key == 'first_name':
                this_thread.current_info['user']['firstname'] = val
            if key == 'last_name':
                this_thread.current_info['user']['lastname'] = val


def create_user(email, password, privileges=None, info=None):
    """Create a new user account on the server.

    Requires ``admin`` privileges or the ``create_user`` permission.

    Args:
        email (str): The e-mail address for the new account.
        password (str): The password for the new account.
        privileges (str or list, optional): A privilege name or list of
            privilege names to assign to the new user.
        info (dict, optional): Additional profile information such as
            ``first_name``, ``last_name``, ``country``, etc.

    Returns:
        int: The user ID of the newly created account.
    """
    return server.create_user(email, password, privileges=privileges, info=info)


def invite_user(email_address, privilege=None, send=True):
    """Create an invitation for a user to register an account.

    Generates a registration token for the given e-mail address.  Requires
    ``admin`` privileges or the ``create_user`` permission.

    Args:
        email_address (str): The e-mail address to invite.
        privilege (str, optional): A privilege to assign when the user
            registers. Defaults to the ordinary user privilege.
        send (bool, optional): If ``True`` (default), sends an invitation
            e-mail and returns ``None``.  If ``False``, returns the
            registration URL instead.

    Returns:
        str or None: The registration URL when ``send=False``, otherwise
            ``None``.
    """
    return server.invite_user(email_address, privilege=privilege, send=send)


def get_user_secret(username, password):
    """Return the decryption key for a user account if the credentials are valid.

    Used to obtain the encryption key required for :func:`get_session_variables`
    and :func:`set_session_variables` when the target interview uses
    server-side encryption.

    Args:
        username (str): The user's e-mail address.
        password (str): The user's password.

    Returns:
        str or None: The decryption key string if the credentials are valid,
            otherwise ``None``.
    """
    return server.get_secret(username, password)


def create_session(yaml_filename, secret=None, url_args=None):
    """Create a new interview session and return its session ID.

    Args:
        yaml_filename (str): The interview filename (e.g.
            ``'docassemble.demo:data/questions/questions.yml'``).
        secret (str, optional): The encryption key for the session. If
            not provided, the current user's key is used.
        url_args (dict, optional): URL arguments to make available in
            the new session via ``url_args``.

    Returns:
        str: The session ID of the newly created session.
    """
    if secret is None:
        secret = this_thread.current_info.get('secret', None)
    (encrypted, session_id) = server.create_session(yaml_filename, secret, url_args=url_args)  # pylint: disable=assignment-from-none,unpacking-non-sequence
    if secret is None and encrypted:
        raise DAError("create_session: the interview is encrypted but you did not provide a secret.")
    return session_id


def get_session_variables(yaml_filename, session_id, secret=None, simplify=True):
    """Return the interview dictionary for the specified session.

    Cannot be used to retrieve variables from the current session.

    Args:
        yaml_filename (str): The interview filename.
        session_id (str): The session ID.
        secret (str, optional): The encryption key for decrypting the
            session. Uses the current user's key if not provided.
        simplify (bool, optional): If ``True``, returns a simplified
            JSON-serializable dictionary. Defaults to ``True``.

    Returns:
        dict: The interview session dictionary.
    """
    if session_id == get_uid() and yaml_filename == this_thread.current_info.get('yaml_filename', None):
        raise DAError("You cannot get variables from the current interview session")
    if secret is None:
        secret = this_thread.current_info.get('secret', None)
    return server.get_session_variables(yaml_filename, session_id, secret=secret, simplify=simplify)


def set_session_variables(yaml_filename, session_id, variables, secret=None, question_name=None, overwrite=False, process_objects=False, delete=None):
    """Set variables in the interview dictionary of another session.

    Cannot be used to modify the current session.

    Args:
        yaml_filename (str): The interview filename.
        session_id (str): The session ID.
        variables (dict): A dictionary mapping variable name strings to
            their new values.
        secret (str, optional): The encryption key for the session.
        question_name (str, optional): The ID of a mandatory question to
            mark as answered.
        overwrite (bool, optional): If ``True``, overwrites the previous
            step instead of creating a new one. Defaults to ``False``.
        process_objects (bool, optional): If ``True``, treats the
            dictionary as a serializable representation of docassemble
            objects. Defaults to ``False``.
        delete (str or list, optional): Variable name(s) to undefine in
            the session.
    """
    if session_id == get_uid() and yaml_filename == this_thread.current_info.get('yaml_filename', None):
        raise DAError("You cannot set variables in the current interview session")
    if secret is None:
        secret = this_thread.current_info.get('secret', None)
    if delete is not None:
        if isinstance(delete, str):
            delete = [delete]
        else:
            delete = list(delete)
    server.set_session_variables(yaml_filename, session_id, variables, secret=secret, del_variables=delete, question_name=question_name, post_setting=not overwrite, process_objects=process_objects)


def run_action_in_session(yaml_filename, session_id, action, arguments=None, secret=None, persistent=False, overwrite=False, read_only=False):
    """Run an action in a different interview session.

    Cannot be used on the current session.

    Args:
        yaml_filename (str): The interview filename.
        session_id (str): The session ID of the target session.
        action (str): The name of the action (event) to run.
        arguments (dict, optional): Arguments to pass to the action.
        secret (str, optional): The encryption key for the session.
        persistent (bool, optional): If ``True``, the action can ask
            questions. Defaults to ``False``.
        overwrite (bool, optional): If ``True``, overwrites the previous
            step. Defaults to ``False``.
        read_only (bool, optional): If ``True``, the session is not saved
            after the action. Defaults to ``False``.

    Returns:
        bool: ``True`` on success.

    Raises:
        DAError: If the action fails or targets the current session.
    """
    if session_id == get_uid() and yaml_filename == this_thread.current_info.get('yaml_filename', None):
        raise DAError("You cannot run an action in the current interview session")
    if arguments is None:
        arguments = {}
    if secret is None:
        secret = this_thread.current_info.get('secret', None)
    result = server.run_action_in_session(i=yaml_filename, session=session_id, secret=secret, action=action, persistent=persistent, overwrite=overwrite, read_only=read_only, arguments=arguments)
    if isinstance(result, dict):
        if result['status'] == 'success':
            return True
        raise DAError("run_action_in_session: " + result['message'])
    return True


def get_question_data(yaml_filename, session_id, secret=None):
    """Return data about the current question for the specified interview session.

    Cannot be used on the current session.

    Args:
        yaml_filename (str): The interview filename.
        session_id (str): The session ID.
        secret (str, optional): The encryption key for decrypting the
            session. Uses the current user's key if not provided.

    Returns:
        dict: A dictionary containing data about the current question.
    """
    if session_id == get_uid() and yaml_filename == this_thread.current_info.get('yaml_filename', None):
        raise DAError("You cannot get question data from the current interview session")
    if secret is None:
        secret = this_thread.current_info.get('secret', None)
    return server.get_question_data(yaml_filename, session_id, secret)


def go_back_in_session(yaml_filename, session_id, secret=None):
    """Go back one step in a different interview session.

    Has the same effect as the user clicking the Back button in that session.
    Cannot be used on the current session.

    Args:
        yaml_filename (str): The interview filename.
        session_id (str): The session ID.
        secret (str, optional): The encryption key for the session.
    """
    if session_id == get_uid() and yaml_filename == this_thread.current_info.get('yaml_filename', None):
        raise DAError("You cannot go back in the current interview session")
    if secret is None:
        secret = this_thread.current_info.get('secret', None)
    server.go_back_in_session(yaml_filename, session_id, secret=secret)


def turn_to_at_sign(match):
    return '@' * len(match.group(1))


def redact(text):
    """Return a redacted version of the text for use in documents.

    Replaces the text with a redaction mark unless redaction has been
    disabled for the current document (e.g., via ``redact: False``).

    Args:
        text (str): The text to potentially redact.

    Returns:
        str: The original text if redaction is disabled, or a redacted
            version (masking characters appropriate for the output format)
            if redaction is enabled.
    """
    if not this_thread.misc.get('redact', True):
        return text
    the_text = str(text)
    the_text = re.sub(r'\[(NBSP|ENDASH|EMDASH|HYPHEN|CHECKBOX|PAGENUM|TOTALPAGES|SECTIONNUM)\]', 'x', the_text)
    ref_text = the_text
    ref_text = re.sub(r'(\[(INDENTBY) [^\]]*\])', turn_to_at_sign, ref_text)
    ref_text = re.sub(r'(\[(START_INDENTATION|STOP_INDENTATION|BEGIN_CAPTION|VERTICAL_LINE|END_CAPTION|BEGIN_TWOCOL|BREAK|END_TWOCOL|TIGHTSPACING|SINGLESPACING|DOUBLESPACING|ONEANDAHALFSPACING|TRIPLESPACING|BLANK|BLANKFILL|PAGEBREAK|SKIPLINE|VERTICALSPACE|NEWLINE|NEWPAR|BR|TAB|END|BORDER|NOINDENT|FLUSHLEFT|FLUSHRIGHT|CENTER|BOLDCENTER)\])', turn_to_at_sign, ref_text)
    ref_text = re.sub(r'(\<\/w\:t\>\<w\:br\/\>\<w\:t xml\:space\=\"preserve\"\>)', turn_to_at_sign, ref_text)
    ref_text = re.sub(r'[\n\r\t]', '@', ref_text)
    ref_text = re.sub(r'[^\@]', '#', ref_text)
    output = ''
    if this_thread.evaluation_context == 'pdf':
        for indexno, char in enumerate(the_text):
            if ref_text[indexno] == '@':
                output += char
            elif re.match(r'[0-9\-]', char):
                output += 'x'
            elif random.random() < 0.2:
                output += ' '
            else:
                output += 'x'
    elif this_thread.evaluation_context == 'docx':
        for indexno, char in enumerate(the_text):
            if ref_text[indexno] == '@':
                output += char
            elif char == ' ':
                output += "\u200B"
            else:
                output += '█'
    else:
        current_word = ''
        for indexno, char in enumerate(the_text):
            if ref_text[indexno] == '@':
                if len(current_word) > 0:
                    output += '[REDACTION_WORD ' + str(current_word) + ']'
                    current_word = ''
                output += char
            elif char == ' ':
                if len(current_word) > 0:
                    output += '[REDACTION_WORD ' + str(current_word) + ']'
                    current_word = ''
                output += '[REDACTION_SPACE]'
            else:
                if char == ']':
                    current_word += '['
                else:
                    current_word += char
        if len(current_word) > 0:
            output += '[REDACTION_WORD ' + str(current_word) + ']'
    return output


def ensure_definition(*pargs, **kwargs):
    for val in pargs:
        if isinstance(val, Undefined):
            str(val)
    for val in kwargs.values():
        if isinstance(val, Undefined):
            str(val)


def verbatim(text):
    """Return the text with special formatting characters escaped for the current output context.

    Prevents Markdown, HTML, or LaTeX characters in user-supplied input from
    being interpreted as formatting codes when rendered on screen or in a
    document.

    Args:
        text (str): The text to escape.

    Returns:
        str: The text with formatting characters escaped appropriately for
            the current output context (Markdown, HTML, DOCX, or LaTeX).
    """
    if this_thread.evaluation_context in ('pandoc tex', 'pandoc pdf'):
        return '\\textrm{' + str(escape_latex(re.sub(r'\r?\n(\r?\n)+', '\n', str(text).strip()))) + '}'
    if this_thread.evaluation_context is None:
        text = '<span>' + re.sub(r'>', '&gt;', re.sub(r'<', '&lt;', re.sub(r'&(?!#?[0-9A-Za-z]+;)', '&amp;', str(text).strip()))) + '</span>'
        text = re.sub(r'\*', r'&#42;', text)
        text = re.sub(r'\_', r'&#95;', text)
        text = re.sub(r'(?<!&)\#', r'&#35;', text)
        text = re.sub(r'\=', r'&#61;', text)
        text = re.sub(r'\+', r'&#43;', text)
        text = re.sub(r'\-', r'&#45;', text)
        text = re.sub(r'([0-9])\.', r'\1&#46;', text)
        return re.sub(r'\r?\n(\r?\n)+', '<br>', text)
    if this_thread.evaluation_context == 'docx':
        return re.sub(r'>', '&gt;', re.sub(r'<', '&lt;', re.sub(r'&(?!#?[0-9A-Za-z]+;)', '&amp;', str(text))))
    return text


class DALocalFile:

    def __init__(self, local_path):
        self.local_path = local_path

    def path(self):
        return self.local_path

    def get_alt_text(self):
        if hasattr(self, 'alt_text'):
            return str(self.alt_text)
        return None

    def set_alt_text(self, alt_text):
        self.alt_text = alt_text


def forget_result_of(*pargs):
    """Reset the result of one or more blocks so they will run again.

    Used to re-ask questions with embedded blocks, or to re-run mandatory
    code blocks, by clearing the record of whether those blocks have been
    completed.

    Args:
        *pargs: The ``id`` strings of the blocks whose results should be
            forgotten.
    """
    the_pargs = unpack_pargs(pargs)
    for id_name in the_pargs:
        key = 'ID ' + id_name
        for key_item in list(this_thread.internal['answers'].keys()):
            if key_item == key or key_item.startswith(key + '|WITH|'):
                del this_thread.internal['answers'][key_item]
        if key in this_thread.internal['answered']:
            this_thread.internal['answered'].remove(key)


def re_run_logic():
    """Stop execution and re-evaluate all initial and mandatory blocks from the beginning.

    Raises a ``ForcedReRun`` exception so that docassemble restarts the
    evaluation of interview logic.  Useful after making variable changes that
    should cause earlier blocks to run again.  Take care to avoid infinite
    loops.
    """
    raise ForcedReRun()


def intrinsic_name_of(var_name, the_user_dict=None):
    if the_user_dict is None:
        the_user_dict = get_user_dict()
    from docassemble.base.util import DAObject  # pylint: disable=import-outside-toplevel
    expression_as_list = [x for x in match_brackets_or_dot.split(var_name) if x != '']
    n = len(expression_as_list)
    i = n
    while i > 0:
        try:
            item = eval(var_name, the_user_dict)
            if isinstance(item, DAObject) and item.has_nonrandom_instance_name:
                var_name = item.instanceName
                break
        except:
            pass
        i -= 1
        var_name = ''.join(expression_as_list[0:i])
    return var_name + (''.join(expression_as_list[i:n]))


def intrinsic_names_of(*pargs, the_user_dict=None):
    if the_user_dict is None:
        the_user_dict = get_user_dict()
    output = []
    for parg in pargs:
        if isinstance(parg, str):
            output.append(intrinsic_name_of(parg, the_user_dict=the_user_dict))
        elif isinstance(parg, dict):
            if len(parg) == 1 and ('undefine' in parg or 'invalidate' in parg or 'recompute' in parg or 'follow up' in parg):
                new_dict = {}
                for key, item in parg.items():
                    if isinstance(item, str):
                        new_dict[key] = intrinsic_name_of(item, the_user_dict=the_user_dict)
                    if isinstance(item, list):
                        new_dict[key] = [intrinsic_name_of(subitem, the_user_dict=the_user_dict) if isinstance(subitem, str) else subitem for subitem in item]
                if len(new_dict):
                    output.append(new_dict)
                else:
                    output.append(parg)
            else:
                output.append(parg)
        else:
            output.append(parg)
    return output


def reconsider(*pargs, evaluate=False):
    """Undefine and re-evaluate one or more variables, ensuring fresh values.

    Each variable is undefined and then immediately re-sought.  A variable
    is only reconsidered once per page load, even if called multiple times.

    Args:
        *pargs: Variable name strings to reconsider.
        evaluate (bool, optional): If ``True``, resolves alias variable
            names to their intrinsic names before reconsidering. Defaults
            to ``False``.
    """
    if 'reconsidered' not in this_thread.misc:
        this_thread.misc['reconsidered'] = set()
    pargs = unpack_pargs(pargs)
    if evaluate:
        pargs = intrinsic_names_of(*pargs)
    for var in pargs:
        if var in this_thread.misc['reconsidered']:
            continue
        undefine(var)
        this_thread.misc['reconsidered'].add(var)
        value(var)


def single_to_double_newlines(text):
    """Convert single newlines to double newlines so each line break becomes a paragraph break.

    Useful when user-supplied text uses single newlines as paragraph
    separators, but the Markdown renderer requires double newlines.

    Args:
        text (str): The text to convert.

    Returns:
        str: The text with each sequence of newline characters replaced by
            two newlines.
    """
    return re.sub(r'[\n\r]+', r'\n\n', str(text))


def secure_filename(the_filename):
    the_filename = normalize("NFKD", the_filename).encode("ascii", "ignore").decode("ascii")
    for sep in (os.path.sep, os.path.altsep):
        if sep:
            the_filename = the_filename.replace(sep, "_")
    the_filename = re.sub(r'[^A-Za-z0-9_\.\- ]', '', the_filename)
    the_filename = re.sub(r'^[\._]*', '', the_filename)
    the_filename = re.sub(r'[\._]*$', '', the_filename)
    return the_filename


def secure_filename_unicode_ok(the_filename):
    for sep in (os.path.sep, os.path.altsep):
        if sep:
            the_filename = the_filename.replace(sep, "_")
    the_filename = re.sub(r'[^\w_\.\- ]', '', the_filename, flags=re.UNICODE)
    the_filename = re.sub(r'^[\._]*', '', the_filename)
    the_filename = re.sub(r'[\._]*$', '', the_filename)
    return the_filename

custom_types = {}


class CustomDataTypeRegister(type):

    def __init__(cls, name, bases, orig_clsdict):
        clsdict = copy.copy(orig_clsdict)
        if len(cls.mro()) > 2:
            if 'name' in clsdict and isinstance(clsdict['name'], str) and not re.search(r'[^a-z0-9A-Z\-\_]', clsdict['name']):
                dataname = clsdict['name']
                new_type = {}
                for base in bases:
                    if base is not CustomDataType:
                        for attr in ('container_class', 'input_class', 'input_type', 'javascript', 'jq_rule', 'jq_message', 'parameters', 'code_parameters', 'mako_parameters', 'skip_if_empty', 'is_object'):
                            if attr not in clsdict and hasattr(base, attr):
                                clsdict[attr] = getattr(base, attr)
                new_type['container_class'] = clsdict.get('container_class', 'da-field-container-datatype-' + dataname)
                new_type['input_class'] = clsdict.get('input_class', 'da' + dataname)
                new_type['input_type'] = clsdict.get('input_type', 'text')
                new_type['javascript'] = clsdict.get('javascript', None)
                new_type['jq_rule'] = clsdict.get('jq_rule', None)
                new_type['jq_message'] = clsdict.get('jq_message', None)
                new_type['parameters'] = clsdict.get('parameters', [])
                new_type['code_parameters'] = clsdict.get('code_parameters', [])
                new_type['mako_parameters'] = clsdict.get('mako_parameters', [])
                new_type['skip_if_empty'] = bool(clsdict.get('skip_if_empty', True))
                new_type['is_object'] = bool(clsdict.get('is_object', False))
                new_type['class'] = cls
                custom_types[dataname] = new_type
        super().__init__(name, bases, clsdict)


class CustomDataType(metaclass=CustomDataTypeRegister):
    include_variable_name = False

    @classmethod
    def validate(cls, item):  # pylint: disable=unused-argument
        return True

    @classmethod
    def call_validate(cls, item, variable_name, data):  # pylint: disable=unused-argument
        if cls.validate.__code__.co_argcount == 4:
            return cls.validate(item, variable_name, data)
        if cls.validate.__code__.co_argcount == 3:
            return cls.validate(item, variable_name)
        return cls.validate(item)

    @classmethod
    def transform(cls, item):
        return item

    @classmethod
    def call_transform(cls, item, variable_name, data):
        if cls.transform.__code__.co_argcount == 4:
            return cls.transform(item, variable_name, data)
        if cls.transform.__code__.co_argcount == 3:
            return cls.transform(item, variable_name)
        return cls.transform(item)

    @classmethod
    def default_for(cls, item):
        return str(item)

    @classmethod
    def call_default_for(cls, item, variable_name, data):
        if cls.default_for.__code__.co_argcount == 4:
            return cls.default_for(item, variable_name, data)
        if cls.default_for.__code__.co_argcount == 3:
            return cls.default_for(item, variable_name)
        return cls.default_for(item)

    @classmethod
    def empty(cls):
        return None


class ServerContext:
    pass

server_context = ServerContext()
server_context.context = 'web'


def get_action_stack():
    try:
        stack = copy.deepcopy(this_thread.internal['event_stack'][this_thread.current_info['user']['session_uid']])
    except:
        stack = []
    return [item for item in reversed(stack) if 'breadcrumb' in item]
