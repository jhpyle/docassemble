# -*- coding: utf-8 -*-
import types
import markdown
from mdx_smartypants import SmartypantsExt
import pattern.en
import re
#import operator
import os
import shutil
import inspect
import mimetypes
import locale
import pkg_resources
import titlecase
from docassemble.base.logger import logmessage
from docassemble.base.error import ForcedNameError, QuestionError, ResponseError, CommandError, BackgroundResponseError, BackgroundResponseActionError
import locale
import decimal
import urllib
import codecs
import copy
import base64
import json
import ast
import datetime
import threading
import astunparse
import sys
import tzlocal
import us
import pycountry
from user_agents import parse as ua_parse
import phonenumbers
locale.setlocale(locale.LC_ALL, '')

__all__ = ['alpha', 'roman', 'item_label', 'ordinal', 'ordinal_number', 'comma_list', 'word', 'get_language', 'set_language', 'get_dialect', 'set_country', 'get_country', 'get_locale', 'set_locale', 'comma_and_list', 'need', 'nice_number', 'quantity_noun', 'currency_symbol', 'verb_past', 'verb_present', 'noun_plural', 'noun_singular', 'indefinite_article', 'capitalize', 'space_to_underscore', 'force_ask', 'period_list', 'name_suffix', 'currency', 'static_image', 'title_case', 'url_of', 'process_action', 'url_action', 'get_info', 'set_info', 'get_config', 'prevent_going_back', 'qr_code', 'action_menu_item', 'from_b64_json', 'defined', 'value', 'message', 'response', 'json_response', 'command', 'background_response', 'background_response_action', 'single_paragraph', 'quote_paragraphs', 'location_returned', 'location_known', 'user_lat_lon', 'interview_url', 'interview_url_action', 'interview_url_as_qr', 'interview_url_action_as_qr', 'interview_email', 'get_emails', 'action_arguments', 'action_argument', 'get_default_timezone', 'user_logged_in', 'user_privileges', 'user_has_privilege', 'user_info', 'task_performed', 'task_not_yet_performed', 'mark_task_as_performed', 'times_task_performed', 'set_task_counter', 'background_action', 'background_response', 'background_response_action', 'us', 'set_live_help_status', 'chat_partners_available', 'phone_number_in_e164', 'phone_number_is_valid', 'countries_list', 'country_name', 'write_record', 'read_records', 'delete_record', 'variables_as_json', 'all_variables', 'language_from_browser', 'device', 'plain', 'bold', 'italic', 'subdivision_type', 'indent', 'raw', 'fix_punctuation', 'set_progress', 'get_progress', 'referring_url', 'undefine', 'dispatch', 'yesno', 'noyes', 'phone_number_part', 'log', 'encode_name', 'decode_name', 'interview_list', 'interview_menu', 'server_capabilities', 'session_tags', 'get_chat_log', 'get_user_list', 'get_user_info', 'set_user_info', 'get_user_secret', 'get_session_variables', 'set_session_variables', 'go_back_in_session', 'manage_privileges']

# debug = False
# default_dialect = 'us'
# default_language = 'en'
# default_locale = 'US.utf8'
# default_country = 'US'

# try:
#     default_timezone = tzlocal.get_localzone().zone
# except:
#     default_timezone = 'America/New_York'
# daconfig = dict()
smartyext = SmartypantsExt(configs=dict())
dot_split = re.compile(r'([^\.\[\]]+(?:\[.*?\])?)')
newlines = re.compile(r'[\r\n]+')
single_newline = re.compile(r'[\r\n]')

class RawValue(object):
    def __init__(self, value):
        self.value = value

def raw(val):
    """This function is only used when passing values to a docx template
    file.  It causes a value to be passed as-is, so that it can be
    used by Jinja2 template code, for example as a list, rather than
    being converted to text.

    """
    return RawValue(val)
        
class ReturnValue(object):
    def __init__(self, **kwargs):
        self.extra = kwargs.get('extra', None)
        self.value = kwargs.get('value', None)
        for key, value in kwargs.iteritems():
            if key not in ['extra', 'value']:
                setattr(self, key, value)
    def __str__(self):
        if hasattr(self, 'ok') and self.ok and hasattr(self, 'content'):
            return self.content
        if hasattr(self, 'error_message'):
            return str(self.error_message)
        return str(self.value)
    def __unicode__(self):
        return unicode(self.__str__())

def get_current_variable():
    if len(this_thread.current_variable):
        return this_thread.current_variable[-1]
    return None

def reset_context():
    this_thread.evaluation_context = None
    this_thread.docx_include_count = 0
    this_thread.docx_template = None

def set_context(new_context, template=None):
    this_thread.evaluation_context = new_context
    this_thread.docx_include_count = 0
    this_thread.docx_template = template

def set_current_variable(var):
    #logmessage("set_current_variable: " + str(var))
    # if len(this_thread.current_variable) > 0 and this_thread.current_variable[-1] == var:
    #     return
    this_thread.current_variable.append(var)

def pop_current_variable():
    #logmessage("pop_current_variable: " + str(this_thread.current_variable))
    if len(this_thread.current_variable):
        var = this_thread.current_variable.pop()
        #logmessage("pop_current_variable: " + str(var))
        return var
    #logmessage("pop_current_variable: None")
    return None

def close_files():
    while len(this_thread.open_files):
        file_object = this_thread.open_files.pop()
        file_object.commit()
    # while len(this_thread.temporary_resources):
    #     the_resource = this_thread.temporary_resources.pop()
    #     if os.path.isdir(the_resource):
    #         shutil.rmtree(the_resource)
    #     elif os.path.isfile(the_resource):
    #         os.remove(the_resource)
            
def set_gathering_mode(mode, instanceName):
    #logmessage("set_gathering_mode: " + str(instanceName) + " with mode " + str(mode))
    if mode:
        if instanceName not in this_thread.gathering_mode:
            #logmessage("set_gathering_mode: using " + str(get_current_variable()))
            this_thread.gathering_mode[instanceName] = get_current_variable()
    else:
        del this_thread.gathering_mode[instanceName]

def get_gathering_mode(instanceName):
    #logmessage("get_gathering_mode: " + str(instanceName))
    if instanceName not in this_thread.gathering_mode:
        return False
    return True

def reset_gathering_mode(*pargs):
    #logmessage("reset_gathering_mode: " + repr([y for y in pargs]))
    if len(pargs) == 0:
        this_thread.gathering_mode = dict()
        return
    var = pargs[0]
    todel = list()
    for instanceName, curVar in this_thread.gathering_mode.iteritems():
        if curVar == var:
            todel.append(instanceName)
    for item in todel:
        del this_thread.gathering_mode[item]

def set_uid(uid):
    this_thread.session_id = uid

def get_uid():
    if this_thread.session_id is not None:
        return this_thread.session_id
    try:
        return this_thread.current_info['session']
    except:
        return None

def get_chat_log(utc=False, timezone=None):
    """Returns the messages in the chat log of the interview."""
    return server.get_chat_log(this_thread.current_info.get('yaml_filename', None), this_thread.current_info.get('session', None), this_thread.current_info.get('secret', None), utc=utc, timezone=timezone)
    
def get_url_start():
    if this_thread.current_info.get('url_root', None) is not None:
        url_start = re.sub(r'/$', r'', this_thread.current_info['url_root'])
    else:
        url_start = get_config('url root')
        if url_start is None:
            url_start = 'http://localhost'
        url_start = re.sub(r'/$', r'', url_start)
        root = get_config('root')
        if root is None:
            root = '/'
        url_start += root
    return url_start

def get_url_root():
    if this_thread.current_info.get('url_root', None) is not None:
        url_root = re.sub(r'/$', r'', this_thread.current_info['url_root'])
    else:
        url_root = get_config('url root')
        if url_root is None:
            url_root = 'http://localhost'
        url_root = re.sub(r'/$', r'', url_root)
    return url_root

def get_current_package():
    if this_thread.current_package is not None:
        return this_thread.current_package
    return None

def get_current_question():
    if this_thread.current_question is not None:
        return this_thread.current_question
    return None

def user_logged_in():
    """Returns True if the user is logged in, False otherwise."""
    if this_thread.current_info['user']['is_authenticated']:
        return True
    return False

def device(ip=False):
    """Returns an object describing the device the user is using, or the
    user's IP address if the optional keyword argument 'ip' is
    True.

    """
    if ip:
        return this_thread.current_info['clientip']
    if 'headers' in this_thread.current_info:
        ua_string = this_thread.current_info['headers'].get('User-Agent', None)
        if ua_string is not None:
            response = ua_parse(ua_string)
        else:
            response = None
    else:
        response = None
    return response

def language_from_browser(*pargs):
    """Attempts to determine the user's language based on information supplied by the user's web browser."""
    if len(pargs) > 0:
        restrict = True
        valid_options = [lang for lang in pargs]
    else:
        restrict = False
    if 'headers' in this_thread.current_info:
        langs = [entry.split(";")[0].strip() for entry in this_thread.current_info['headers'].get('Accept-Language', '').lower().split(",")]
    else:
        return None
    for lang in langs:
        if restrict:
            if lang in valid_options:
                return lang
            else:
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
            else:
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
    """Given a two-digit country code, returns the country name."""
    return pycountry.countries.get(alpha_2=country_code).name

def state_name(state_code, country_code=None):
    """Given a two-digit U.S. state abbreviation or the abbreviation of a
    subdivision of another country, returns the state/subdivision
    name."""
    if country_code is None:
        country_code = 'US'
    for subdivision in pycountry.subdivisions.get(country_code=country_code):
        m = re.search(r'-([A-Z]+)$', subdivision.code)
        if m and m.group(1) == state_code:
            return subdivision.name
    #return us.states.lookup(state_code).name

def subdivision_type(country_code):
    """Returns the name of the most common country subdivision type for
    the given country code."""
    counts = dict()
    for subdivision in pycountry.subdivisions.get(country_code=country_code):
        if subdivision.parent_code is not None:
            continue
        if subdivision.name not in counts:
            counts[subdivision.type] = 1
        else:
            counts[subdivision.type] += 1
    counts_ordered = sorted(counts.keys(), key=lambda x: counts[x], reverse=True)
    if len(counts_ordered) > 1 and counts[counts_ordered[1]] > 1:
        return counts_ordered[0] + '/' + counts_ordered[1]
    elif len(counts_ordered) > 0:
        return counts_ordered[0]
    else:
        return None
    
def countries_list():
    """Returns a list of countries, suitable for use in a multiple choice field."""
    return [{country.alpha_2: country.name} for country in sorted(pycountry.countries, key=lambda x: x.name)]

def states_list(country_code=None):
    """Returns a list of U.S. states or subdivisions of another country,
    suitable for use in a multiple choice field."""
    if country_code is None:
        country_code = 'US'
    mapping = dict()
    for subdivision in pycountry.subdivisions.get(country_code=country_code):
        if subdivision.parent_code is not None:
            continue
        m = re.search(r'-([A-Z0-9]+)$', subdivision.code)
        if m:
            mapping[m.group(1)] = subdivision.name
    return mapping

def interface():
    """Returns web, json, sms, cron, or worker, depending on how the interview is being accessed."""
    return this_thread.current_info.get('interface', None)

def user_privileges():
    """Returns a list of the user's privileges.  For users who are not 
    logged in, this is always ['user']."""
    if user_logged_in():
        return [role for role in this_thread.current_info['user']['roles']]
    else:
        return [word('user')]
    return False

def user_has_privilege(*pargs):
    """Given a privilege or a list of privileges, returns True if the user 
    has any of the privileges, False otherwise."""
    privileges = list()
    for parg in pargs:
        if type(parg) is list:
            arg_list = parg
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

class TheUser:
    def name(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name
        if self.last_name:
            return self.last_name
        if self.first_name:
            return self.first_name
        return word("Unnamed User")
    def __str__(self):
        return self.name()
    def __unicode__(self):
        return unicode(self.__str__())

def user_info():
    """Returns an object with information from the user profile.  Keys 
    include first_name, last_name, email, country, subdivision_first, 
    subdivision_second, subdivision_third, and organization."""
    user = TheUser()
    if user_logged_in():
        user.first_name = this_thread.current_info['user']['firstname']
        user.last_name = this_thread.current_info['user']['lastname']
        user.email = this_thread.current_info['user']['email']
        user.country = this_thread.current_info['user']['country']
        user.subdivision_first = this_thread.current_info['user']['subdivisionfirst']
        user.subdivision_second = this_thread.current_info['user']['subdivisionsecond']
        user.subdivision_third = this_thread.current_info['user']['subdivisionthird']
        user.organization = this_thread.current_info['user']['organization']
    else:
        user.first_name = word("Anonymous")
        user.last_name = word("User")
    user.session = get_uid()
    user.filename = this_thread.current_info.get('yaml_filename', None)
    return user

def action_arguments():
    """Used when processing an "action."  Returns a dictionary with the 
    arguments passed to url_action() or interview_url_action()."""
    if 'arguments' in this_thread.current_info:
        return this_thread.current_info['arguments']
    else:
        return dict()

def action_argument(item):
    """Used when processing an "action."  Returns the value of the given 
    argument, which is assumed to have been passed to url_action() or 
    interview_url_action()."""
    if 'arguments' in this_thread.current_info:
        return this_thread.current_info['arguments'].get(item, None)
    else:
        return None

def location_returned():
    """Returns True or False depending on whether an attempt has yet 
    been made to transmit the user's GPS location from the browser to 
    docassemble.  Will return true even if the attempt was not successful 
    or the user refused to consent to the transfer."""
    #logmessage("Location returned")
    if 'user' in this_thread.current_info:
        #logmessage("user exists")
        if 'location' in this_thread.current_info['user']:
            #logmessage("location exists")
            #logmessage("Type is " + str(type(this_thread.current_info['user']['location'])))
            pass
    if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and type(this_thread.current_info['user']['location']) is dict:
        return True
    return False

def location_known():
    """Returns True or False depending on whether docassemble was able to learn the user's
    GPS location through the web browser."""
    if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and type(this_thread.current_info['user']['location']) is dict and 'latitude' in this_thread.current_info['user']['location']:
        return True
    return False

def user_lat_lon():
    """Returns the user's latitude and longitude as a tuple."""
    if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and type(this_thread.current_info['user']['location']) is dict:
        if 'latitude' in this_thread.current_info['user']['location'] and 'longitude' in this_thread.current_info['user']['location']:
            return this_thread.current_info['user']['location']['latitude'], this_thread.current_info['user']['location']['longitude']
        elif 'error' in this_thread.current_info['user']['location']:
            return this_thread.current_info['user']['location']['error'], this_thread.current_info['user']['location']['error']
    return None, None

def chat_partners_available(*pargs, **kwargs):
    """Given a list of partner roles, returns the number of operators and 
    peers available to chat with the user."""
    partner_roles = kwargs.get('partner_roles', list())
    mode = kwargs.get('mode', 'peerhelp')
    if type(partner_roles) is not list:
        partner_roles = [partner_roles]
    for parg in pargs:
        if type(parg) is not list:
            the_parg = [parg]
        else:
            the_parg = parg
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
        return dict(peer=0, help=0)
    return server.chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles)

def interview_email(key=None, index=None):
    """Returns an e-mail address that can be used to send e-mail messages to the case"""
    if key is None and index is not None:
        raise DAError("interview_email: if you provide an index you must provide a key")
    domain = server.daconfig.get('incoming mail domain', server.daconfig.get('external hostname', server.hostname))
    return server.get_short_code(key=key, index=index) + '@' + domain

def get_emails(key=None, index=None):
    """Returns a data structure representing existing e-mail addresses for the interview and any e-mails sent to those e-mail addresses"""
    return server.retrieve_emails(key=None, index=None)

def interview_url(**kwargs):
    """Returns a URL that is direct link to the interview and the current
    variable store.  This is used in multi-user interviews to invite
    additional users to participate."""
    do_local = False
    args = dict()
    for key, val in kwargs.iteritems():
        args[key] = val
    if 'local' in args:
        if args['local']:
            do_local = True
        del args['local']
    if 'i' in args:
        if 'session' not in args:
            args['from_list'] = 1
    else:
        args['i'] = this_thread.current_info['yaml_filename']
        args['session'] = this_thread.current_info['session']
    if do_local:
        url = get_config('root')
        if url is None:
            url = '/'
    else:
        url = str(this_thread.internal['url'])
    url += '?' + '&'.join(map((lambda (k, v): str(k) + '=' + urllib.quote(str(v))), args.iteritems()))
    return url

def set_title(**kwargs):
    """Sets the title of the interview that is displayed in the navigation
    bar and other places, as well as other features of the navigation bar.

    """
    this_thread.internal['short title'] = kwargs.get('short', None)
    this_thread.internal['tab title'] = kwargs.get('tab', None)
    for key, val in kwargs.iteritems():
        key = re.sub(r'_', r' ', key)
        if key in ('title', 'logo', 'subtitle', 'exit link', 'exit label'):
            this_thread.internal[key] = val

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
    def __hash__(self, the_object):
        return this_thread.internal['tags'].__hash__(the_object)
    def __str__(self):
        return str(this_thread.internal['tags'])
    def __unicode__(self):
        return unicode(this_thread.internal['tags'])
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
    """Returns the set of tags with which the interview and session have
    been tagged.

    """
    if 'tags' not in this_thread.internal:
        this_thread.internal['tags'] = set()
        for metadata in this_thread.interview.metadata:
            if 'tags' in metadata and type(metadata['tags']) is list:
                for tag in metadata['tags']:
                    this_thread.internal['tags'].add(tag)
    return DATagsSet()
    
def interview_url_action(action, **kwargs):
    """Like interview_url, except it additionally specifies an action.
    The keyword arguments are arguments to the action, except for the keyword
    arguments local, i, and session, which are used the way they are used in 
    interview_url"""
    do_local = False
    if 'local' in kwargs:
        if kwargs['local']:
            do_local = True
        del kwargs['local']
    args = dict()
    if 'i' in kwargs:
        args['i'] = kwargs['i']
        del kwargs['i']
    else:
        args['i'] = this_thread.current_info['yaml_filename']
    if 'session' in kwargs:
        args['session'] = kwargs['session']
        del kwargs['session']
    else:
        args['session'] = this_thread.current_info['session']
    args['action'] = myb64quote(json.dumps({'action': action, 'arguments': kwargs}))
    if do_local:
        url = ''
    else:
        url = str(this_thread.internal['url'])
    url += '?' + '&'.join(map((lambda (k, v): str(k) + '=' + urllib.quote(str(v))), args.iteritems()))
    return url

def interview_url_as_qr(**kwargs):
    """Inserts into the markup a QR code linking to the interview.
    This can be used to pass control from a web browser or a paper 
    handout to a mobile device."""
    return qr_code(interview_url(**kwargs))

def interview_url_action_as_qr(action, **kwargs):
    """Like interview_url_as_qr, except it additionally specifies an 
    action.  The keyword arguments are arguments to the action."""
    return qr_code(interview_url_action(action, **kwargs))

def get_info(att):
    """Used to retrieve the values of global variables set through set_info()."""
    if hasattr(this_thread, att):
        return getattr(this_thread, att)
    return None

def set_info(**kwargs):
    """Used to set the values of global variables you wish to retrieve through get_info()."""
    for att, value in kwargs.iteritems():
        setattr(this_thread, att, value)

def set_progress(number):
    """Sets the position of the progress meter."""
    this_thread.internal['progress'] = number

def get_progress():
    """Returns the position of the progress meter."""
    return this_thread.internal['progress']

class DANav(object):
    def __init__(self):
        self.past = set()
        self.sections = None
        self.current = None

    def __str__(self):
        return self.show_sections(style='inline')
    
    def __unicode__(self):
        return unicode(self.__str__())

    def set_section(self, section):
        """Sets the current section in the navigation."""
        if section == self.current:
            return False
        self.current = section
        self.past.add(section)
        return True

    def get_section(self, display=False, language=None):
        """Returns the current section of the navigation."""
        current_section = self.current
        if current_section is None or not display:
            return current_section
        the_sections = self.get_sections(language=language)
        current_title = current_section
        for x in the_sections:
            subitems = None
            if type(x) is dict:
                if len(x) == 2 and 'subsections' in x:
                    for key, val in x.iteritems():
                        if key == 'subsections':
                            subitems = val
                        else:
                            the_key = key
                            the_title = val
                elif len(x) == 1:
                    the_key = x.keys()[0]
                    value = x[the_key]
                    if type(value) is list:
                        subitems = value
                        the_title = the_key
                    else:
                        the_title = value
                else:
                    logmessage("navigation_bar: too many keys in dict.  " + str(the_sections))
                    continue
            else:
                the_key = None
                the_title = unicode(x)
            if (the_key is not None and current_section == the_key) or (the_key is None and current_section == the_title):
                current_title = the_title
                break
            if subitems:
                found_it = False
                for y in subitems:
                    if type(y) is dict:
                        if len(y) == 1:
                            sub_key = y.keys()[0]
                            sub_title = y[sub_key]
                        else:
                            logmessage("navigation_bar: too many keys in dict.  " + str(the_sections))
                            continue
                    else:
                        sub_key = None
                        sub_title = unicode(y)
                    if (sub_key is not None and current_section == sub_key) or (sub_key is None and current_section == sub_title):
                        current_title = sub_title
                        found_it = True
                        break
                if found_it:
                    break
        return current_title

    def set_sections(self, sections, language=None):
        """Sets the sections of the navigation to the given list."""
        if language is None:
            language = this_thread.language
        if sections is None:
            sections = []
        self.sections[language] = sections
        self.past = set()

    def get_sections(self, language=None):
        """Returns the sections of the navigation as a list."""
        if language is None:
            language = this_thread.language
        if language not in self.sections:
            language = '*'
        return self.sections.get(language, list())

    def show_sections(self, style=None, show_links=False):
        """Returns the sections of the navigation as HTML."""
        if style == "inline":
            the_class = 'dainline'
            interior_class = 'dainlineinside'
            li_class = "danavli"
            a_class = "danavlink label label-default label-larger"
            the_js = """
    <script>
      $("a.danavlink").last().addClass('thelast');
      $("a.danavlink").each(function(){
        if ($(this).hasClass('label') && !$(this).hasClass('notavailableyet')){
          var the_li = $(this).parent();
          var the_a = $(this);
          var the_delay = 1000 + 250 * parseInt($(this).data('index'));
          setTimeout(function(){
            $(the_a).addClass('danavlidone');
            $(the_a).removeClass('label-default');
            if ($(the_li).hasClass('active')){
              $(the_a).addClass('label-success');
            }
            else{
              $(the_a).addClass('label-warning');
            }
          }, the_delay);
        }
      });
    </script>
"""
        else:
            the_class = ''
            interior_class = None
            li_class = None
            a_class = None
            the_js = None
        if this_thread.interview_status is not None and the_js is not None:
           this_thread.interview_status.extra_scripts.append(the_js) 
        return '  <div class="dasections"><ul class="' + the_class + '">' + "\n" + server.navigation_bar(self, this_thread.interview, wrapper=False, inner_ul_class=interior_class, li_class=li_class, a_class=a_class, show_links=show_links, show_nesting=False) + '  </ul></div>' + "\n"

word_collection = {
    'es': {
        'Continue': 'Continuar',
        'Help': 'Ayuda',
        'Sign in': 'Registrarse',
        'Sign in or sign up to save answers': 'Inicie sesión o regístrese para guardar las respuestas',
        'Question': 'Interrogación',
        'save_as_multiple': 'The document is available in the following formats:',
        'save_as_singular': 'The document is available in the following format:',
        'pdf_message': 'for printing; requires Adobe Reader or similar application',
        'rtf_message': 'for editing; requires Microsoft Word, Wordpad, or similar application',
        'docx_message': 'for editing; requires Microsoft Word or compatible application',
        'tex_message': 'for debugging PDF output',
        'attachment_message_plural': 'The following documents have been created for you.',
        'attachment_message_singular': 'The following document has been created for you.',
        'Yes': 'Sí',
        'No': 'No'
        },
    'en': {
        'and': "and",
        'or': "or",
        'yes': "yes",
        'no': "no",
        'Document': "Document",
        'content': 'content',
        'Open as:': 'Open this document as:',
        'Open as:': 'Save this documents as:',
        'Question': 'Question',
        'Help': 'Help',
        'Download': 'Download',
        'Preview': 'Preview',
        'Markdown': 'Markdown',
        'Source': 'Source',
        'attachment_message_plural': 'The following documents have been created for you.',
        'attachment_message_singular': 'The following document has been created for you.',
        'save_as_multiple': 'The document is available in the following formats:',
        'save_as_singular': 'The document is available in the following format:',
        'pdf_message': 'for printing; requires Adobe Reader or similar application',
        'rtf_message': 'for editing; requires Microsoft Word, Wordpad, or similar application',
        'docx_message': 'for editing; requires Microsoft Word or compatible application',
        'tex_message': 'for debugging PDF output',
        'vs.': 'vs.',
        'v.': 'v.',
        'Case No.': 'Case No.',
        'In the': 'In the',
        'This field is required.': 'You need to fill this in.',
        "You need to enter a valid date.": "You need to enter a valid date.",
        "You need to enter a complete e-mail address.": "You need to enter a complete e-mail address.",
        "You need to enter a number.": "You need to enter a number.",
        "You need to select one.": "You need to select one.",
        "Country Code": 'Country Code (e.g., "us")',
        "First Subdivision": "State Abbreviation (e.g., 'NY')",
        "Second Subdivision": "County",
        "Third Subdivision": "Municipality",
        "Organization": "Organization",
    }
}

ordinal_numbers = {
    'en': {
        '0': 'zeroth',
        '1': 'first',
        '2': 'second',
        '3': 'third',
        '4': 'fourth',
        '5': 'fifth',
        '6': 'sixth',
        '7': 'seventh',
        '8': 'eighth',
        '9': 'ninth',
        '10': 'tenth'
    },
    'es': {
        '0': 'zeroth',
        '1': 'primero',
        '2': 'segundo',
        '3': 'tercero',
        '4': 'cuarto',
        '5': 'quinto',
        '6': 'sexto',
        '7': 'séptimo',
        '8': 'octavo',
        '9': 'noveno',
        '10': 'décimo'
    }
}

nice_numbers = {
    'en': {
        '0': 'zero',
        '1': 'one',
        '2': 'two',
        '3': 'three',
        '4': 'four',
        '5': 'five',
        '6': 'six',
        '7': 'seven',
        '8': 'eight',
        '9': 'nine',
        '10': 'ten'
    },
    'es': {
        '0': 'cero',
        '1': 'uno',
        '2': 'dos',
        '3': 'tres',
        '4': 'cuatro',
        '5': 'cinco',
        '6': 'seis',
        '7': 'siete',
        '8': 'ocho',
        '9': 'nueve',
        '10': 'diez'
    }
}

# def basic_url_of(*pargs, **kwargs):
#     """Returns a URL to a file within a docassemble package."""
#     return pargs[0]

# the_url_func = basic_url_of

# def url_of(*pargs, **kwargs):
#     """Returns a URL to a file within a docassemble package."""
#     return the_url_func(*pargs, **kwargs)

# def basic_write_record(key, data):
#     return None

class WebFunc(object):
    pass
server = WebFunc()

def null_func(*pargs, **kwargs):
    return None

server.write_record = null_func
server.read_records = null_func
server.delete_record = null_func
server.url_for = null_func
server.generate_csrf = null_func
server.bg_action = null_func
server.worker_convert = null_func
server.chat_partners_available = null_func
server.absolute_filename = null_func
server.save_numbered_file = null_func
server.send_mail = null_func
server.absolute_filename = null_func
server.file_finder = null_func
server.url_finder = null_func
server.user_id_dict = null_func
server.sms_body = null_func
server.get_sms_session = null_func
server.initiate_sms_session = null_func
server.terminate_sms_session = null_func
server.debug = False
server.default_dialect = 'us'
server.default_language = 'en'
server.default_locale = 'US.utf8'
server.default_country = 'US'
server.server_redis = None
server.twilio_config = dict()
server.daconfig = dict()
try:
    server.default_timezone = tzlocal.get_localzone().zone
except:
    server.default_timezone = 'America/New_York'

# class NullWebFunc(object):
#     def write_record(*pargs, **kwargs):
#         return None
#     def read_records(*pargs, **kwargs):
#         return None
#     def delete_record(*pargs, **kwargs):
#         return None
#     def url_for(*pargs, **kwargs):
#         return None
#     def generate_csrf(*pargs, **kwargs):
#         sys.stderr.write("Generating csrf\n")
#         return None
#     def bg_action(*pargs, **kwargs):
#         return None
#     def worker_convert(*pargs, **kwargs):
#         return None
#     def chat_partners(*pargs, **kwargs):
#         return dict(peer=0, help=0)
#     def absolute_filename(*pargs, **kwargs):
#         return None
#     def save_numbered_file(*pargs, **kwargs):
#         return None
#     def send_mail(*pargs, **kwargs):
#         return None
#     def absolute_filename(*pargs, **kwargs):
#         return None
#     def file_finder(*pargs, **kwargs):
#         return None
#     def url_finder(*pargs, **kwargs):
#         return None
#     def user_id_dict(*pargs, **kwargs):
#         return None
#     def __init__(self):
#         self.debug = False
#         self.default_dialect = 'us'
#         self.default_language = 'en'
#         self.default_locale = 'US.utf8'
#         self.default_country = 'US'
#         self.server_redis = None
#         try:
#             self.default_timezone = tzlocal.get_localzone().zone
#         except:
#             self.default_timezone = 'America/New_York'
#         self.daconfig = dict()

# write_record = server.write_record
# read_records = server.read_records
# delete_record = server.delete_record
# url_of = server.url_finder
# get_sms_session = server.get_sms_session
# initiate_sms_session = server.initiate_sms_session
# terminate_sms_session = server.terminate_sms_session

def write_record(key, data):
    """Stores the data in a SQL database for later retrieval with the
    key.  Returns the unique ID integers of the saved record.
    """
    return server.write_record(key, data)
def read_records(key):
    """Returns a dictionary of records that have been stored with
    write_record() using the given key.  In the dictionary, the key is
    the unique ID integer of the record and the value is the data that
    had been stored.
    """
    return server.read_records(key)
def delete_record(key, id):
    """Deletes a record with the given key and id."""
    return server.delete_record(key, id)
def url_of(file_reference, **kwargs):
    """Returns a URL to a file within a docassemble package."""
    if 'package' not in kwargs:
        kwargs['_package'] = get_current_package()
    if 'question' not in kwargs:
        kwargs['_question'] = get_current_question()
    return server.url_finder(file_reference, **kwargs)

def server_capabilities():
    """Returns a dictionary with true or false values indicating various capabilities of the server."""
    result = dict(sms=False, fax=False, google_login=False, facebook_login=False, twitter_login=False, azure_login=False, phone_login=False, voicerss=False, s3=False, azure=False, github=False, pypi=False, googledrive=False, google_maps=False)
    if 'twilio' in server.daconfig and type(server.daconfig['twilio']) in [list, dict]:
        if type(server.daconfig['twilio']) is list:
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
    if 'oauth' in server.daconfig and type(server.daconfig['oauth']) is dict:
        if 'google' in server.daconfig['oauth'] and type(server.daconfig['oauth']['google']) is dict:
            if not ('enable' in server.daconfig['oauth']['google'] and not server.daconfig['oauth']['google']['enable']):
                result['google_login'] = True
        if 'facebook' in server.daconfig['oauth'] and type(server.daconfig['oauth']['facebook']) is dict:
            if not ('enable' in server.daconfig['oauth']['facebook'] and not server.daconfig['oauth']['facebook']['enable']):
                result['facebook_login'] = True
        if 'azure' in server.daconfig['oauth'] and type(server.daconfig['oauth']['azure']) is dict:
            if not ('enable' in server.daconfig['oauth']['azure'] and not server.daconfig['oauth']['azure']['enable']):
                result['azure_login'] = True
        if 'twitter' in server.daconfig['oauth'] and type(server.daconfig['oauth']['twitter']) is dict:
            if not ('enable' in server.daconfig['oauth']['twitter'] and not server.daconfig['oauth']['twitter']['enable']):
                result['twitter_login'] = True
        if 'googledrive' in server.daconfig['oauth'] and type(server.daconfig['oauth']['googledrive']) is dict:
            if not ('enable' in server.daconfig['oauth']['googledrive'] and not server.daconfig['oauth']['googledrive']['enable']):
                result['googledrive'] = True
        if 'github' in server.daconfig['oauth'] and type(server.daconfig['oauth']['github']) is dict:
            if not ('enable' in server.daconfig['oauth']['github'] and not server.daconfig['oauth']['github']['enable']):
                result['github'] = True
    if 'pypi' in server.daconfig and server.daconfig['pypi'] is True:
        result['pypi'] = True
    if 'google' in server.daconfig and type(server.daconfig['google']) is dict and ('google maps api key' in server.daconfig['google'] or 'api key' in server.daconfig['google']):
        result['google_maps'] = True
    for key in ['voicerss', 's3', 'azure']:
        if key in server.daconfig and type(server.daconfig[key]) is dict:
            if not ('enable' in server.daconfig[key] and not server.daconfig[key]['enable']):
                result[key] = True
    return result

# def generate_csrf(*pargs, **kwargs):
#     return server.generate_csrf(*pargs, **kwargs)
# def chat_partners(*pargs, **kwargs):
#     return dict(peer=0, help=0)
# def absolute_filename(*pargs, **kwargs):
#     return server.absolute_filename(*pargs, **kwargs)

def update_server(*pargs, **kwargs):
    for arg, func in kwargs.iteritems():
        #sys.stderr.write("Setting " + str(arg) + "\n")
        if arg == 'bg_action':
            the_func = func
            def worker_wrapper(action, ui_notification, **kwargs):
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
#     return dict()

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

# def basic_delete_record(key, id):
#     return

# the_delete_record = basic_delete_record

# def set_delete_record(func):
#     global the_delete_record
#     the_delete_record = func

# def delete_record(key, id):
#     """Deletes a record with the given key and id."""
#     return the_delete_record(key, id)

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
#     #sys.stderr.write("Got to null worker\n")
#     return None

# bg_action = null_worker

# worker_convert = null_worker

class ThreadVariables(threading.local):
    language = server.default_language
    dialect = server.default_dialect
    country = server.default_country
    locale = server.default_locale
    user = None
    role = 'user'
    current_info = dict()
    internal = dict()
    #user_dict = None
    initialized = False
    redis = None
    session_id = None
    current_package = None
    interview = None
    interview_status = None
    current_question = None
    evaluation_context = None
    docx_template = None
    gathering_mode = dict()
    current_variable = list()
    open_files = set()
    #markdown = markdown.Markdown(extensions=[smartyext, 'markdown.extensions.sane_lists', 'markdown.extensions.tables', 'markdown.extensions.attr_list'], output_format='html5')
    markdown = markdown.Markdown(extensions=[smartyext, 'markdown.extensions.sane_lists', 'markdown.extensions.tables', 'markdown.extensions.attr_list'], output_format='html5')
    #temporary_resources = set()
    saved_files = dict()
    message_log = list()
    misc = dict()
    prevent_going_back = False
    def __init__(self, **kw):
        if self.initialized:
            raise SystemError('__init__ called too many times')
        self.initialized = True
        self.__dict__.update(kw)

this_thread = ThreadVariables()

def backup_thread_variables():
    backup = dict()
    for key in ['language', 'dialect', 'country', 'locale', 'user', 'role', 'current_info', 'internal', 'initialized', 'session_id', 'gathering_mode', 'current_variable']:
        backup[key] = copy.deepcopy(getattr(this_thread, key))
    return backup

def restore_thread_variables(backup):
    for key in ['language', 'dialect', 'country', 'locale', 'user', 'role', 'current_info', 'internal', 'initialized', 'session_id', 'gathering_mode', 'current_variable']:
        setattr(this_thread, key, backup[key])

def background_response(*pargs, **kwargs):
    """Finishes a background task."""
    raise BackgroundResponseError(*pargs, **kwargs)

def background_response_action(*pargs, **kwargs):
    """Finishes a background task by running an action to save values."""
    raise BackgroundResponseActionError(*pargs, **kwargs)

def background_error_action(*pargs, **kwargs):
    """Indicates an action that should be run if the current background task results in an error."""
    this_thread.current_info['on_error'] = dict(action=pargs[0], arguments=kwargs)

def background_action(*pargs, **kwargs):
    """Runs an action in the background."""
    action = pargs[0]
    if len(pargs) > 1:
        ui_notification = pargs[1]
    else:
        ui_notification = None
    return(server.bg_action(action, ui_notification, **kwargs))

class BackgroundResult(object):
    def __init__(self, result):
        for attr in ('value', 'error_type', 'error_trace', 'error_message', 'variables'):
            if hasattr(result, attr):
                setattr(self, attr, getattr(result, attr))
            else:
                setattr(self, attr, None)

class MyAsyncResult(object):
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

def worker_caller(func, ui_notification, action):
    #sys.stderr.write("Got to worker_caller in functions\n")
    result = MyAsyncResult()
    result.obj = func.delay(this_thread.current_info['yaml_filename'], this_thread.current_info['user'], this_thread.current_info['session'], this_thread.current_info['secret'], this_thread.current_info['url'], this_thread.current_info['url_root'], action, extra=ui_notification)
    if ui_notification is not None:
        worker_key = 'da:worker:uid:' + str(this_thread.current_info['session']) + ':i:' + str(this_thread.current_info['yaml_filename']) + ':userid:' + str(this_thread.current_info['user']['the_user_id'])
        #sys.stderr.write("worker_caller: id is " + str(result.obj.id) + " and key is " + worker_key + "\n")
        server.server_redis.rpush(worker_key, result.obj.id)
    #sys.stderr.write("worker_caller: id is " + str(result.obj.id) + "\n")
    return result

# def null_chat_partners(*pargs, **kwargs):
#     return (dict(peer=0, help=0))

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

def default_ordinal_function(i):
    return unicode(i)

def ordinal_function_en(i):
    num = unicode(i)
    if 10 <= i % 100 <= 20:
        return num + 'th'
    elif i % 10 == 3:
        return num + 'rd'
    elif i % 10 == 1:
        return num + 'st'
    elif i % 10 == 2:
        return num + 'nd'
    else:
        return num + 'th'

ordinal_functions = {
    'en': ordinal_function_en,
    '*': ordinal_function_en
}

def fix_punctuation(text, mark=None):
    """Ensures the text ends with punctuation."""
    if mark is None:
        mark = '.'
    text = re.sub(r' +$', r'', text)
    m = re.search(r'[\.\!\?]$', text)
    if m:
        return text
    return text + mark

def item_label(num, level=None, punctuation=True):
    """Given an index and an outline level, returns I., II., A., etc."""
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
    if not punctuation:
        return string
    if level < 3:
        return string + '.'
    elif level == 3 or level == 6:
        return string + ')'
    else:
        return '(' + string + ')'

def alpha(num, case=None):
    """Given an index, returns A, B, C ... Z, AA, AB, etc."""
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
    """Given an index between 0 and 3999, returns a roman numeral between 1 and 4000."""
    if case is None:
        case = 'upper'
    num = num + 1
    if type(num) != type(1):
        raise TypeError, "expected integer, got %s" % type(num)
    if not 0 < num < 4000:
        raise ValueError, "Argument must be between 1 and 3999"   
    ints = (1000, 900, 500,  400, 100,  90, 50,  40, 10,  9,   5,   4,  1)
    nums = ('M',  'CM', 'D', 'CD', 'C','XC','L','XL','X','IX','V','IV','I')
    result = ""
    for i in range(len(ints)):
        count = int(num / ints[i])
        result += nums[i] * count
        num -= ints[i] * count
    if case == 'lower':
        return result.lower()
    return result

def words():
    return word_collection[this_thread.language]

def word(the_word, **kwargs):
    """Returns the word translated into the current language.  If a translation 
    is not known, the input is returned."""
    # Currently, no kwargs are used, but in the future, this function could be
    # expanded to use kwargs.  For example, for languages with gendered words,
    # the gender could be passed as a keyword argument.
    if the_word is True:
        the_word = 'yes'
    elif the_word is False:
        the_word = 'no'
    elif the_word is None:
        the_word = "I don't know"
    try:
        the_word = word_collection[this_thread.language][the_word].decode('utf8')
    except:
        the_word = unicode(the_word)
    if kwargs.get('capitalize', False):
        return capitalize(the_word)
    return the_word

def update_language_function(lang, term, func):
    if term not in language_functions:
        language_functions[term] = dict()
    language_functions[term][lang] = func
    return

def update_nice_numbers(lang, defs):
    if lang not in nice_numbers:
        nice_numbers[lang] = dict()
    for number, word in defs.iteritems():
        nice_numbers[lang][unicode(number)] = word
    return

def update_ordinal_numbers(lang, defs):
    if lang not in ordinal_numbers:
        ordinal_numbers[lang] = dict()
    for number, word in defs.iteritems():
        ordinal_numbers[lang][unicode(number)] = word
    return

def update_ordinal_function(lang, func):
    ordinal_functions[lang] = func
    return

def update_word_collection(lang, defs):
    if lang not in word_collection:
        word_collection[lang] = dict()
    for word, translation in defs.iteritems():
        if translation is not None:
            word_collection[lang][word] = translation
    return

# def set_da_config(config):
#     global daconfig
#     daconfig = config

def get_config(key, none_value=None):
    """Returns a value from the docassemble configuration.  If not
    defined, returns None or the value of the optional keyword
    argument, none_value.

    """
    return server.daconfig.get(key, none_value)

# def set_default_language(lang):
#     global default_language
#     default_language = lang
#     return

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
    """Returns the default timezone (e.g., 'America/New_York').  This is
    the time zone of the server, unless the default timezone is set in
    the docassemble configuration.

    """
    return server.default_timezone

# def reset_thread_local():
#     this_thread.open_files = set()
#     this_thread.temporary_resources = set()

# def reset_thread_variables():
#     this_thread.saved_files = dict()
#     this_thread.message_log = list()

def reset_local_variables():
    this_thread.language = server.default_language
    this_thread.locale = server.default_locale
    this_thread.prevent_going_back = False
    this_thread.gathering_mode = dict()
    this_thread.current_variable = list()
    this_thread.open_files = set()
    this_thread.saved_files = dict()
    this_thread.message_log = list()

def prevent_going_back():
    """Instructs docassemble to disable the user's back button, so that the user cannot
    go back and change any answers before this point in the interview."""
    this_thread.prevent_going_back = True
    return

def set_language(lang, dialect=None):
    """Sets the language to use for linguistic functions.
    E.g., set_language('es') to set the language to Spanish.
    Use the keyword argument "dialect" to set a dialect."""
    if dialect:
        this_thread.dialect = dialect
    elif lang != this_thread.language:
        this_thread.dialect = None
    this_thread.language = lang
    return

def get_language():
    """Returns the current language (e.g., "en")."""
    return this_thread.language

def set_country(country):
    """Sets the current country (e.g., "US")."""
    this_thread.country = country
    return

def get_country():
    """Returns the current country (e.g., "US")."""
    return this_thread.country

def get_dialect():
    """Returns the current dialect."""
    return this_thread.dialect

def set_default_locale(loc):
    global default_locale
    default_locale = loc
    return

def set_locale(loc):
    """Sets the current locale.  See also update_locale()."""
    this_thread.locale = loc
    return

def get_locale():
    """Returns the current locale setting."""
    return this_thread.locale

def update_locale():
    """Updates the system locale based on the value set by set_locale()."""
    try:
        locale.setlocale(locale.LC_ALL, str(this_thread.locale))
    except:
        logmessage("update_locale error: unable to set the locale to " + str(this_thread.locale))
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
    return

def comma_list_en(*pargs, **kwargs):
    """Returns the arguments separated by commas.  If the first argument is a list, 
    that list is used.  Otherwise, the arguments are treated as individual items.
    See also comma_and_list()."""
    if 'comma_string' in kwargs:
        comma_string = kwargs['comma_string']
    else:
        comma_string = ", "
    if (len(pargs) == 0):
        return unicode('')
    elif (len(pargs) == 1):
        if type(pargs[0]) == list:
            pargs = pargs[0]
    if (len(pargs) == 0):
        return unicode('')
    elif (len(pargs) == 1):
        return(unicode(pargs[0]))
    else:
        return(comma_string.join(pargs))

def comma_and_list_es(*pargs, **kwargs):
    if 'and_string' not in kwargs:
        kwargs['and_string'] = 'y'
    return comma_and_list_en(*pargs, **kwargs)

def comma_and_list_en(*pargs, **kwargs):
    """Returns an English-language listing of the arguments.  If the first argument is a list, 
    that list is used.  Otherwise, the arguments are treated as individual items in the list.
    Use the optional argument oxford=False if you do not want a comma before the "and."
    See also comma_list()."""
    if 'oxford' in kwargs and kwargs['oxford'] == False:
        extracomma = ""
    else:
        extracomma = ","
    if 'and_string' in kwargs:
        and_string = kwargs['and_string']
    else:
        and_string = word('and')
    if 'comma_string' in kwargs:
        comma_string = kwargs['comma_string']
    else:
        comma_string = ", "
    if 'before_and' in kwargs:
        before_and = kwargs['before_and']
    else:
        before_and = " "
    if 'after_and' in kwargs:
        after_and = kwargs['after_and']
    else:
        after_and = " "
    if (len(pargs) == 0):
        return unicode('')
    elif (len(pargs) == 1):
        if type(pargs[0]) == list:
            pargs = pargs[0]
        elif type(pargs[0]) == set:
            pargs = list(pargs[0])
    if (len(pargs) == 0):
        return unicode('')
    elif (len(pargs) == 1):
        return(unicode(pargs[0]))
    elif (len(pargs) == 2):
        return(unicode(pargs[0]) + before_and + and_string + after_and + unicode(pargs[1]))
    else:
        return(comma_string.join(map(unicode, pargs[:-1])) + extracomma + before_and + and_string + after_and + unicode(pargs[-1]))

def need(*pargs):
    """Given one or more variables, this function instructs docassemble 
    to do what is necessary to define the variables."""
    for argument in pargs:
        argument
    return True

def pickleable_objects(input_dict):
    output_dict = dict()
    for key in input_dict:
        if type(input_dict[key]) in [types.ModuleType, types.FunctionType, types.TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, types.ClassType, file]:
            continue
        if key == "__builtins__":
            continue
        output_dict[key] = input_dict[key]
    return(output_dict)

def ordinal_number_default(i):
    """Returns the "first," "second," "third," etc. for a given number.
    ordinal_number(1) returns "first."  For a function that can be used
    on index numbers that start with zero, see ordinal()."""
    num = unicode(i)
    if this_thread.language in ordinal_numbers:
        language_to_use = this_thread.language
    elif '*' in ordinal_numbers:
        language_to_use = '*'
    else:
        language_to_use = 'en'
    if num in ordinal_numbers[language_to_use]:
        return ordinal_numbers[language_to_use][num]
    if this_thread.language in ordinal_functions:
        language_to_use = this_thread.language
    elif '*' in ordinal_functions:
        language_to_use = '*'
    else:
        language_to_use = 'en'
    return ordinal_functions[language_to_use](i)

def salutation_default(indiv, with_name=False, with_name_and_punctuation=False):
    """Returns Mr., Ms., etc. for an individual."""
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
        elif with_name:
            return salut_and_name
    return salut

def ordinal_default(j, **kwargs):
    """Returns the "first," "second," "third," etc. for a given number, which is expected to
    be an index starting with zero.  ordinal(0) returns "first."  For a more literal ordinal 
    number function, see ordinal_number()."""
    result = ordinal_number(int(float(j)) + 1)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(result)
    return result

def nice_number_default(num, capitalize=False):
    """Returns the number as a word in the current language."""
    if this_thread.language in nice_numbers:
        language_to_use = this_thread.language
    elif '*' in nice_numbers:
        language_to_use = '*'
    else:
        language_to_use = 'en'
    if int(float(num)) == float(num):
        num = int(float(num))
    if unicode(num) in nice_numbers[language_to_use]:
        the_word = nice_numbers[language_to_use][unicode(num)]
        if capitalize:
            return capitalize_function(the_word)
        else:
            return the_word
    elif type(num) is int:
        return unicode(locale.format("%d", num, grouping=True))
    else:
        return unicode(locale.format("%.2f", float(num), grouping=True)).rstrip('0')

def quantity_noun_default(num, noun, as_integer=True, capitalize=False):
    if as_integer:
        num = int(round(num))
    result = nice_number(num) + " " + noun_plural(noun, num)
    if capitalize:
        return capitalize_function(result)
    else:
        return result

def capitalize_default(a):
    if a and (type(a) is str or type(a) is unicode) and len(a) > 1:
        return(a[0].upper() + a[1:])
    else:
        return(unicode(a))

def currency_symbol_default():
    """Returns the currency symbol for the current locale."""
    return locale.localeconv()['currency_symbol'].decode('utf8')

def currency_default(value, decimals=True):
    """Returns the value as a currency, according to the conventions of the current locale.
    Use the optional keyword argument decimals=False if you do not want to see decimal places
    in the number."""
    obj_type = type(value).__name__
    if obj_type in ['FinancialList', 'PeriodicFinancialList']:
        value = value.total()
    elif obj_type in ['Value', 'PeriodicValue']:
        if value.exists:
            value = value.amount()
        else:
            value = 0
    try:
        float(value)
    except:
        return ''
    if decimals:
        return locale.currency(float(value), symbol=True, grouping=True).decode('utf8')
    else:
        return currency_symbol() + locale.format("%d", int(float(value)), grouping=True)

def prefix_constructor(prefix):
    def func(word, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(unicode(prefix)) + unicode(word)
        else:
            return unicode(prefix) + unicode(word)
    return func

def double_prefix_constructor_reverse(prefix_one, prefix_two):
    def func(word_one, word_two, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(unicode(prefix_one)) + unicode(word_two) + unicode(prefix_two) + unicode(word_one)
        else:
            return unicode(prefix_one) + unicode(word_two) + unicode(prefix_two) + unicode(word_one)
    return func

def prefix_constructor_two_arguments(prefix, **kwargs):
    def func(word_one, word_two, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(unicode(prefix)) + unicode(word_one) + ' ' + unicode(word_two)
        else:
            return unicode(prefix) + unicode(word_one) + ' ' + unicode(word_two)
    return func

def middle_constructor(middle, **kwargs):
    def func(a, b, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(unicode(a)) + unicode(middle) + unicode(b)
        else:
            return unicode(a) + unicode(middle) + unicode(b)
    return func

def possessify_en(a, b, **kwargs):
    if 'plural' in kwargs and kwargs['plural']:
        middle = "' "
    else:
        middle = "'s "
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(unicode(a)) + unicode(middle) + unicode(b)
    else:
        return unicode(a) + unicode(middle) + unicode(b)

def a_preposition_b_default(a, b, **kwargs):
    #logmessage("Got here")
    if hasattr(a, 'preposition'):
        #logmessage("Has preposition")
        preposition = a.preposition
    else:
        preposition = word('in the')
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(unicode(a)) + unicode(' ' + preposition + ' ') + unicode(b)
    else:
        return unicode(a) + unicode(' ' + preposition + ' ') + unicode(b)

def verb_present_en(*pargs, **kwargs):
    new_args = list()
    for arg in pargs:
        new_args.append(unicode(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    output = pattern.en.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return(capitalize(output))
    else:
        return(output)
    
def verb_past_en(*pargs, **kwargs):
    new_args = list()
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    output = pattern.en.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return(capitalize(output))
    else:
        return(output)

def noun_plural_en(*pargs, **kwargs):
    noun = noun_singular_en(pargs[0])
    if len(pargs) >= 2 and pargs[1] == 1:
        return unicode(noun)
    output = pattern.en.pluralize(unicode(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return(capitalize(output))
    else:
        return(output)

def noun_singular_en(*pargs, **kwargs):
    if len(pargs) >= 2 and pargs[1] != 1:
        return pargs[0]
    output = pattern.en.singularize(unicode(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return(capitalize(output))
    else:
        return(output)

def indefinite_article_en(*pargs, **kwargs):
    output = pattern.en.article(*pargs, **kwargs) + " " + unicode(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return(capitalize(output))
    else:
        return(output)

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
    'her': {
        'en': prefix_constructor('her ')
    },
    'his': {
        'en': prefix_constructor('his ')
    },
    'is_word': {
        'en': prefix_constructor('is ')
    },
    'their': {
        'en': prefix_constructor('their ')
    },
    'of_the': {
        'en': prefix_constructor('of the ')
    },
    'your': {
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
    'did_a_b': {
        'en': prefix_constructor_two_arguments('did ')
    },
    'do_you': {
        'en': prefix_constructor('do you ')
    },
    'did_you': {
        'en': prefix_constructor('did you ')
    },
    'were_you': {
        'en': prefix_constructor('were you ')
    },
    'was_a_b': {
        'en': prefix_constructor_two_arguments('was ')
    },
    'have_you': {
        'en': prefix_constructor('have you ')
    },
    'has_a_b': {
        'en': prefix_constructor_two_arguments('has ')
    },
    'verb_past': {
        'en': lambda *pargs, **kwargs: verb_past_en(*pargs, **kwargs)
    },
    'verb_present': {
        'en': lambda *pargs, **kwargs: verb_present_en(*pargs, **kwargs)
    },
    'noun_plural': {
        'en': lambda *pargs, **kwargs: noun_plural_en(*pargs, **kwargs)
    },
    'noun_singular': {
        'en': lambda *pargs, **kwargs: noun_singular_en(*pargs, **kwargs)
    },
    'indefinite_article': {
        'en': indefinite_article_en
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
        'es': comma_and_list_es
    },
    'comma_list': {
        'en': comma_list_en
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
        '*': titlecase.titlecase
    },
    'salutation': {
        '*': salutation_default
    }
}

def language_function_constructor(term):
    if term not in language_functions:
        raise SystemError("term " + str(term) + " not in language_functions")
    def func(*args, **kwargs):
        if this_thread.language in language_functions[term]:
            return language_functions[term][this_thread.language](*args, **kwargs)
        if '*' in language_functions[term]:
            return language_functions[term]['*'](*args, **kwargs)
        if 'en' in language_functions[term]:
            logmessage("Term " + str(term) + " is not defined for language " + str(this_thread.language))
            return language_functions[term]['en'](*args, **kwargs)
        raise SystemError("term " + str(term) + " not defined in language_functions for English or *")
    return func
    
in_the = language_function_constructor('in_the')
a_preposition_b = language_function_constructor('a_preposition_b')
a_in_the_b = language_function_constructor('a_in_the_b')
her = language_function_constructor('her')
his = language_function_constructor('his')
is_word = language_function_constructor('is_word')
their = language_function_constructor('their')
your = language_function_constructor('your')
its = language_function_constructor('its')
of_the = language_function_constructor('of_the')
the = language_function_constructor('the')
this = language_function_constructor('this')
these = language_function_constructor('these')
do_you = language_function_constructor('do_you')
did_you = language_function_constructor('did_you')
does_a_b = language_function_constructor('does_a_b')
did_a_b = language_function_constructor('did_a_b')
were_you = language_function_constructor('were_you')
was_a_b = language_function_constructor('was_a_b')
have_you = language_function_constructor('have_you')
has_a_b = language_function_constructor('has_a_b')
verb_past = language_function_constructor('verb_past')
verb_present = language_function_constructor('verb_present')
noun_plural = language_function_constructor('noun_plural')
noun_singular = language_function_constructor('noun_singular')
some = language_function_constructor('some')
indefinite_article = language_function_constructor('indefinite_article')
period_list = language_function_constructor('period_list')
name_suffix = language_function_constructor('name_suffix')
currency = language_function_constructor('currency')
currency_symbol = language_function_constructor('currency_symbol')
possessify = language_function_constructor('possessify')
possessify_long = language_function_constructor('possessify_long')
comma_list = language_function_constructor('comma_list')
comma_and_list = language_function_constructor('comma_and_list')
nice_number = language_function_constructor('nice_number')
quantity_noun = language_function_constructor('quantity_noun')
capitalize = language_function_constructor('capitalize')
capitalize_function = capitalize
title_case = language_function_constructor('title_case')
ordinal_number = language_function_constructor('ordinal_number')
ordinal = language_function_constructor('ordinal')
salutation = language_function_constructor('salutation')

if verb_past.__doc__ is None:
    verb_past.__doc__ = """Given a verb, returns the past tense of the verb."""
if verb_present.__doc__ is None:
    verb_present.__doc__ = """Given a verb, returns the present tense of the verb."""
if noun_plural.__doc__ is None:
    noun_plural.__doc__ = """Given a noun, returns the plural version of the noun, unless the optional second argument indicates a quantity of 1."""
if noun_singular.__doc__ is None:
    noun_singular.__doc__ = """Given a noun, returns the singular version of the noun, unless the optional second argument indicates a quantity other than 1."""
if indefinite_article.__doc__ is None:
    indefinite_article.__doc__ = """Given a noun, returns the noun with an indefinite article attached
                                 (e.g., indefinite_article("fish") returns "a fish")."""
if capitalize.__doc__ is None:
    capitalize.__doc__ = """Capitalizes the first letter of the word or phrase."""
if period_list.__doc__ is None:
    period_list.__doc__ = """Returns an array of arrays where the first element of each array is a number, 
                          and the second element is a word expressing what that numbers means as a per-year
                          period.  This is meant to be used in code for a multiple-choice field."""
if name_suffix.__doc__ is None:
    name_suffix.__doc__ = """Returns an array of choices for the suffix of a name.
                          This is meant to be used in code for a multiple-choice field."""
if period_list.__doc__ is None:
    period_list.__doc__ = """Returns a list of periods of a year, for inclusion in dropdown items."""
if name_suffix.__doc__ is None:
    name_suffix.__doc__ = """Returns a list of name suffixes, for inclusion in dropdown items."""
if currency.__doc__ is None:
    currency.__doc__ = """Formats the argument as a currency value, according to language and locale."""
if currency_symbol.__doc__ is None:
    currency_symbol.__doc__ = """Returns the symbol for currency, according to the locale."""
if possessify.__doc__ is None:
    possessify.__doc__ = """Given two arguments, a and b, returns "a's b." """
if possessify_long.__doc__ is None:
    possessify_long.__doc__ = """Given two arguments, a and b, returns "the b of a." """
if comma_list.__doc__ is None:
    comma_list.__doc__ = """Returns the arguments separated by commas."""
if comma_and_list.__doc__ is None:
    comma_and_list.__doc__ = """Returns the arguments separated by commas with "and" before the last one."""
if nice_number.__doc__ is None:
    nice_number.__doc__ = """Takes a number as an argument and returns the number as a word if ten or below."""
if quantity_noun.__doc__ is None:
    quantity_noun.__doc__ = """Takes a number and a singular noun as an argument and returns the number as a word if ten or below, followed by the noun in a singular or plural form depending on the number."""
if capitalize.__doc__ is None:
    capitalize.__doc__ = """Returns the argument with the first letter capitalized."""
if title_case.__doc__ is None:
    title_case.__doc__ = """Returns the argument with the first letter of each word capitalized, as in a title."""
if ordinal_number.__doc__ is None:
    ordinal_number.__doc__ = """Given a number, returns "first" or "23rd" for 1 or 23, respectively."""
if ordinal.__doc__ is None:
    ordinal.__doc__ = """Given a number that is expected to be an index, returns "first" or "23rd" for 0 or 22, respectively."""

def underscore_to_space(a):
    return(re.sub('_', ' ', unicode(a)))

def space_to_underscore(a):
    """Converts spaces in the input to underscores in the output.  Useful for making filenames without spaces."""
    return(re.sub(' +', '_', unicode(a).encode('ascii', errors='ignore')))

def message(*pargs, **kwargs):
    """Presents a screen to the user with the given message."""
    raise QuestionError(*pargs, **kwargs)
    
def response(*pargs, **kwargs):
    """Sends a custom HTTP response."""
    raise ResponseError(*pargs, **kwargs)

def json_response(data):
    """Sends data in JSON format as an HTTP response."""
    raise ResponseError(json.dumps(data, sort_keys=True, indent=2) + "\n", content_type="application/json")

def variables_as_json():
    """Sends an HTTP response with all variables in JSON format."""
    raise ResponseError(None, all_variables=True)

def all_variables(simplify=True):
    """Returns the interview variables as a dictionary suitable for export to JSON or other formats."""
    if simplify:
        return serializable_dict(get_user_dict())
    return pickleable_objects(get_user_dict())

def command(*pargs, **kwargs):
    """Executes a command, such as exit, logout, restart, or leave."""
    raise CommandError(*pargs, **kwargs)

def force_ask(*pargs):
    """Given a variable name, instructs docassemble to ask a question that
    would define the variable, even if the variable has already been
    defined.  This does not change the interview logic, but merely
    diverts from the interview logic, temporarily, in order to attempt
    to ask a question.  If more than one variable name is provided,
    questions will be asked serially.

    """
    raise ForcedNameError(*pargs)

def force_ask_nameerror(variable_name):
    raise NameError("name '" + str(variable_name) + "' is not defined")

def force_gather(*pargs):
    """Like force_ask(), except more insistent.  In addition to making a 
    single attempt to ask a question that offers to define the variable, 
    it enlists the process_action() function to seek the definition of 
    the variable.  The process_action() function will keep trying to define
    the variable until it is defined."""
    for variable_name in pargs:
        if variable_name not in this_thread.internal['gather']:
            this_thread.internal['gather'].append(variable_name)
    raise ForcedNameError(variable_name)

def static_filename_path(filereference):
    result = package_data_filename(static_filename(filereference))
    #if result is None or not os.path.isfile(result):
    #    result = server.absolute_filename("/playgroundstatic/" + re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filereference)).path
    return(result)

def static_filename(filereference):
    if re.search(r',', filereference):
        return(None)
    #filereference = re.sub(r'^None:data/static/', '', filereference)
    #filereference = re.sub(r'^None:', '', filereference)
    parts = filereference.split(':')
    if len(parts) < 2:
        parts = ['docassemble.base', filereference]
    if re.search(r'\.\./', parts[1]):
        return(None)
    if not re.match(r'(data|static)/.*', parts[1]):
        parts[1] = 'data/static/' + parts[1]
    return(parts[0] + ':' + parts[1])

def static_image(filereference, **kwargs):
    """Inserts appropriate markup to include a static image.  If you know
    the image path, you can just use the "[FILE ...]" markup.  This function is
    useful when you want to assemble the image path programmatically.
    Takes an optional keyword argument "width"
    (e.g., static_image('docassemble.demo:crawling.png', width='2in'))."""
    filename = static_filename(filereference)
    if filename is None:
        return('ERROR: invalid image reference')
    width = kwargs.get('width', None)
    if width is None:
        return('[FILE ' + filename + ']')
    else:
        return('[FILE ' + filename + ', ' + width + ']')

def qr_code(string, **kwargs):
    """Inserts appropriate markup to include a QR code image.  If you know
    the string you want to encode, you can just use the "[QR ...]" markup.  
    This function is useful when you want to assemble the string programmatically.
    Takes an optional keyword argument "width"
    (e.g., qr_code('https://google.com', width='2in'))."""
    width = kwargs.get('width', None)
    if width is None:
        return('[QR ' + string + ']')
    else:
        return('[QR ' + string + ', ' + width + ']')

def standard_template_filename(the_file):
    try:
        return(pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.base'), "docassemble/base/data/templates/" + str(the_file)))
    except:
        #logmessage("Error retrieving data file\n")
        return(None)

def package_template_filename(the_file, **kwargs):
    the_file = the_file.strip()
    parts = the_file.split(":")
    if len(parts) == 1:
        package = kwargs.get('package', None)
        if package is not None:
            parts = [package, the_file]
    if len(parts) == 2:
        m = re.search(r'^docassemble.playground([0-9]+)$', parts[0])
        if m:
            parts[1] = re.sub(r'^data/templates/', '', parts[1])
            return(server.absolute_filename("/playgroundtemplate/" + m.group(1) + '/' + re.sub(r'[^A-Za-z0-9\-\_\. ]', '', parts[1])).path)
        if not re.match(r'data/.*', parts[1]):
            parts[1] = 'data/templates/' + parts[1]
        try:
            return(pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1]))
        except:
            return(None)
    return(None)

def standard_question_filename(the_file):
    return(pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.base'), "docassemble/base/data/questions/" + str(the_file)))
    return(None)

def package_data_filename(the_file):
    #logmessage("package_data_filename with: " + str(the_file))
    if the_file is None:
        return(None)
    #the_file = re.sub(r'^None:data/static/', '', the_file)
    #the_file = re.sub(r'^None:', '', the_file)
    parts = the_file.split(":")
    result = None
    #if len(parts) == 1:
    #    parts = ['docassemble.base', the_file]
    if len(parts) == 2:
        m = re.search(r'^docassemble.playground([0-9]+)$', parts[0])
        if m:
            if re.search(r'^data/sources/', parts[1]):
                parts[1] = re.sub(r'^data/sources/', '', parts[1])
                return(server.absolute_filename("/playgroundsources/" + m.group(1) + '/' + re.sub(r'[^A-Za-z0-9\-\_\. ]', '', parts[1])).path)
            parts[1] = re.sub(r'^data/static/', '', parts[1])
            return(server.absolute_filename("/playgroundstatic/" + m.group(1) + '/' + re.sub(r'[^A-Za-z0-9\-\_\. ]', '', parts[1])).path)
        try:
            result = pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1])
        except:
            result = None
    #if result is None or not os.path.isfile(result):
    #    result = server.absolute_filename("/playgroundstatic/" + re.sub(r'[^A-Za-z0-9\-\_\.]', '', the_file)).path
    return(result)

def package_question_filename(the_file):
    parts = the_file.split(":")
    #if len(parts) == 1:
    #    parts = ['docassemble.base', the_file]
    if len(parts) == 2:
        if not re.match(r'data/.*', parts[1]):
            parts[1] = 'data/questions/' + parts[1]
        try:
            return(pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1]))
        except:
            return(None)
    return(None)

# def default_absolute_filename(the_file):
#     return the_file

# absolute_filename = default_absolute_filename

# def set_absolute_filename(func):
#     #logmessage("Running set_absolute_filename in util")
#     global absolute_filename
#     absolute_filename = func
#     return

def nodoublequote(text):
    return re.sub(r'"', '', unicode(text))

def process_action():
    """If an action is waiting to be processed, it processes the action."""
    #sys.stderr.write("process_action() started")
    if 'action' not in this_thread.current_info:
        to_be_gathered = [variable_name for variable_name in this_thread.internal['gather']]
        for variable_name in to_be_gathered:
            if defined(variable_name):
                this_thread.internal['gather'].remove(variable_name)
            else:
                force_ask_nameerror(variable_name)
        return
    #sys.stderr.write("process_action() continuing")
    the_action = this_thread.current_info['action']
    del this_thread.current_info['action']
    if the_action == 'need':
        for key in ['variable', 'variables']:
            if key in this_thread.current_info['arguments']:
                if type(this_thread.current_info['arguments'][key]) is list:
                    for var in this_thread.current_info['arguments'][key]:
                        if var not in this_thread.internal['gather']:
                            this_thread.internal['gather'].append(var)
                elif this_thread.current_info['arguments'][key] not in this_thread.internal['gather']:
                    this_thread.internal['gather'].append(this_thread.current_info['arguments'][key])
                del this_thread.current_info['arguments'][key]
        to_be_gathered = [variable_name for variable_name in this_thread.internal['gather']]
        for variable_name in to_be_gathered:
            if defined(variable_name):
                this_thread.internal['gather'].remove(variable_name)
            else:
                force_ask_nameerror(variable_name)
        return        
    force_ask(the_action)

def url_action(action, **kwargs):
    """Returns a URL to run an action in the interview."""
    return '?action=' + urllib.quote(myb64quote(json.dumps({'action': action, 'arguments': kwargs}))) + '&i=' + this_thread.current_info['yaml_filename']

def myb64quote(text):
    return codecs.encode(text.encode('utf8'), 'base64').decode().replace('\n', '')

# def set_debug_status(new_value):
#     global debug
#     debug = new_value

def debug_status():
    return server.debug
# grep -E -R -o -h "word\(['\"][^\)]+\)" * | sed "s/^[^'\"]+['\"]//g"

def action_menu_item(label, action, **kwargs):
    """Takes two arguments, a label and an action, and optionally takes
    keyword arguments that are passed on to the action.  The label is
    what the user will see and the action is the action that will be
    performed when the user clicks on the item in the menu.  This is
    only used when setting the special variable menu_items.  E.g.,
    menu_items = [ action_menu_item('Ask for my favorite food',
    'favorite_food') ]

    """
    return dict(label=label, url=url_action(action, **kwargs))

def from_b64_json(string):
    """Converts the string from base-64, then parses the string as JSON, and returns the object.
    This is an advanced function that is used by software developers to integrate other systems 
    with docassemble."""
    if string is None:
        return None
    return json.loads(base64.b64decode(string))

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

def components_of(full_variable):
    node = ast.parse(full_variable, mode='eval')
    crawler = lister()
    crawler.visit(node)
    return list(reversed(crawler.stack))

def get_user_dict():
    frame = inspect.stack()[1][0]
    the_user_dict = frame.f_locals
    while '_internal' not in the_user_dict:
        frame = frame.f_back
        if frame is None:
            return dict()
        if 'user_dict' in frame.f_locals:
            the_user_dict = eval('user_dict', frame.f_locals)
            if '_internal' in the_user_dict:
                break
            else:
                return None
        else:
            the_user_dict = frame.f_locals
    return the_user_dict

def undefine(var):
    """Deletes the variable"""
    if type(var) not in [str, unicode]:
        raise Exception("undefine() must be given a string, not " + str(var) + ", a " + str(var.__class__.__name__))
    try:
        eval(var, dict())
        return False
    except:
        pass
    frame = inspect.stack()[1][0]
    components = components_of(var)
    if len(components) == 0 or len(components[0]) < 2:
        raise Exception("undefine: variable " + str(var) + " is not a valid variable name")
    variable = components[0][1]
    the_user_dict = frame.f_locals
    while variable not in the_user_dict:
        frame = frame.f_back
        if frame is None:
            return False
        if 'user_dict' in frame.f_locals:
            the_user_dict = eval('user_dict', frame.f_locals)
            if variable in the_user_dict:
                break
            else:
                return False
        else:
            the_user_dict = frame.f_locals
    try:
        exec('del ' + var, the_user_dict)
    except:
        pass

def dispatch(var):
    """Shows a menu screen."""
    if type(var) not in [str, unicode]:
        raise Exception("dispatch() must be given a string")
    while value(var) != 'None':
        value(value(var))
        undefine(value(var))
        undefine(var)
    undefine(var)
    return True

def define(var, val):
    """Sets the given variable, expressed as a string, to the given value."""
    if type(var) not in [str, unicode]:
        raise Exception("define() must be given a string as the variable name")
    user_dict = get_user_dict()
    if user_dict is None:
        raise Exception("define: could not find interview answers")
    # Trigger exceptions for the left hand side before creating __define_val
    exec(var + " = None", user_dict)
    user_dict['__define_val'] = val
    exec(var + " = __define_val", user_dict)
    if '__define_val' in user_dict:
        del user_dict['__define_val']

def defined(var):
    """Returns true if the variable has already been defined.  Otherwise, returns false."""
    if type(var) not in [str, unicode]:
        raise Exception("defined() must be given a string")
    try:
        eval(var, dict())
        return True
    except:
        pass
    frame = inspect.stack()[1][0]
    components = components_of(var)
    if len(components) == 0 or len(components[0]) < 2:
        raise Exception("defined: variable " + str(var) + " is not a valid variable name")
    variable = components[0][1]
    the_user_dict = frame.f_locals
    while variable not in the_user_dict:
        frame = frame.f_back
        if frame is None:
            return False
        if 'user_dict' in frame.f_locals:
            the_user_dict = eval('user_dict', frame.f_locals)
            if variable in the_user_dict:
                break
            else:
                return False
        else:
            the_user_dict = frame.f_locals
    if variable not in the_user_dict:
        return False
    if len(components) == 1:
        return True
    cum_variable = ''
    for elem in components:
        if elem[0] == 'name':
            cum_variable += elem[1]
            continue
        elif elem[0] == 'attr':
            to_eval = "hasattr(" + cum_variable + ", " + repr(elem[1]) + ")"
            cum_variable += '.' + elem[1]
        elif elem[0] == 'index':
            try:
                the_index = eval(elem[1], the_user_dict)
            except:
                return False
            if type(the_index) == int:
                to_eval = 'len(' + cum_variable + ') > ' + str(the_index)
            else:
                to_eval = elem[1] + " in " + cum_variable
            cum_variable += '[' + elem[1] + ']'
        try:
            result = eval(to_eval, the_user_dict)
        except:
            return False
        if result:
            continue
        return False
    return True

def value(var):
    """Returns the value of the variable given by the string 'var'."""
    if type(var) not in [str, unicode]:
        raise Exception("value() must be given a string")
    try:
        return eval(var, dict())
    except:
        pass
    if re.search(r'[\(\)\n\r]|lambda', var):
        raise Exception("value() is invalid")
    frame = inspect.stack()[1][0]
    components = components_of(var)
    if len(components) == 0 or len(components[0]) < 2:
        raise Exception("value: variable " + str(var) + " is not a valid variable name")
    variable = components[0][1]
    the_user_dict = frame.f_locals
    while variable not in the_user_dict:
        frame = frame.f_back
        if frame is None:
            force_ask(var)
        if 'user_dict' in frame.f_locals:
            the_user_dict = eval('user_dict', frame.f_locals)
            if variable in the_user_dict:
                break
            else:
                force_ask(var)
        else:
            the_user_dict = frame.f_locals
    if variable not in the_user_dict:
        force_ask(var)
    if len(components) == 1:
        return eval(variable, the_user_dict)
    cum_variable = ''
    for elem in components:
        if elem[0] == 'name':
            cum_variable += elem[1]
            continue
        elif elem[0] == 'attr':
            to_eval = "hasattr(" + cum_variable + ", " + repr(elem[1]) + ")"
            cum_variable += '.' + elem[1]
        elif elem[0] == 'index':
            try:
                the_index = eval(elem[1], the_user_dict)
            except:
                force_ask(var)
            if type(the_index) == int:
                to_eval = 'len(' + cum_variable + ') > ' + str(the_index)
            else:
                to_eval = elem[1] + " in " + cum_variable
            cum_variable += '[' + elem[1] + ']'
        try:
            result = eval(to_eval, the_user_dict)
        except:
            force_ask(var)
        if result:
            continue
        force_ask(var)
    return eval(cum_variable, the_user_dict)

# def _undefine(*pargs):
#     logmessage("called _undefine")
#     for var in pargs:
#         _undefine(var)

# def undefine(var):
#     """Makes the given variable undefined."""
#     logmessage("called undefine")
#     if type(var) not in [str, unicode]:
#         raise Exception("undefine() must be given one or more strings")
#     components = components_of(var)
#     variable = components[0][1]
#     frame = inspect.stack()[1][0]
#     the_user_dict = frame.f_locals
#     while variable not in the_user_dict:
#         frame = frame.f_back
#         if frame is None:
#             return
#         if 'user_dict' in frame.f_locals:
#             the_user_dict = eval('user_dict', frame.f_locals)
#             if variable in the_user_dict:
#                 break
#             else:
#                 return
#         else:
#             the_user_dict = frame.f_locals
#     try:
#         exec("del " + var, the_user_dict)
#     except:
#         logmessage("Failed to delete " + var)
#         pass
#     return

def single_paragraph(text):
    """Reduces the text to a single paragraph.  Useful when using Markdown 
    to indent user-supplied text."""
    return newlines.sub(' ', text)

def quote_paragraphs(text):
    """Adds Markdown to quote all paragraphs in the text."""
    return '> ' + single_newline.sub('\n> ', unicode(text).strip())

def task_performed(task):
    """Returns True if the task has been performed at least once, otherwise False."""
    if task in this_thread.internal['tasks'] and this_thread.internal['tasks'][task]:
        return True
    return False

def task_not_yet_performed(task):
    """Returns True if the task has never been performed, otherwise False."""
    if task_performed(task):
        return False
    return True

def mark_task_as_performed(task):
    """Increases by 1 the number of times the task has been performed."""
    if not task in this_thread.internal['tasks']:
        this_thread.internal['tasks'][task] = 0
    this_thread.internal['tasks'][task] += 1
    return this_thread.internal['tasks'][task]

def times_task_performed(task):
    """Returns the number of times the task has been performed."""
    if not task in this_thread.internal['tasks']:
        return 0
    return this_thread.internal['tasks'][task]

def set_task_counter(task, times):
    """Allows you to manually set the number of times the task has been performed."""
    this_thread.internal['tasks'][task] = times

def set_live_help_status(availability=None, mode=None, partner_roles=None):
    """Defines whether live help features are available, the mode of chat,
    the roles that the interview user will assume in the live chat
    system, and the roles of people with which the interview user
    would like to live chat.

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
        for parg in partner_roles:
            if type(parg) is list:
                plist = parg
            else:
                plist = [parg]
            for arg in plist:
                new_roles.add(arg)
        this_thread.internal['livehelp']['partner_roles'] = list(new_roles)

def phone_number_in_e164(number, country=None):
    """Given a phone number and a country code, returns the number in
    E.164 format.  Returns None if the number could not be so formatted."""
    if country is None:
        country = get_country()
    try:
        pn = phonenumbers.parse(number, country)
        output = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
    except:
        return None
    return output
        
def phone_number_is_valid(number, country=None):
    """Given a phone number and a country code, returns True if the phone number is valid, otherwise False."""
    if country is None:
        country = get_country()
    try:
        pn = phonenumbers.parse(number, country)
    except:
        return False
    if phonenumbers.is_possible_number(pn) and phonenumbers.is_valid_number(pn):
        return True
    return False

def phone_number_part(number, part, country=None):
    if country is None:
        country = get_country()
    try:
        pn = phonenumbers.parse(number, country)
    except:
        return ''
    formatted_number = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)
    parts = [x for x in re.split(r'[^0-9]+', formatted_number) if re.search(r'[0-9]', x)]
    if part < len(parts):
        return parts[part]
    else:
        return ''

def dict_as_json(user_dict):
    return json.dumps(serializable_dict(user_dict))

def serializable_dict(user_dict):
    result_dict = dict()
    for key, data in user_dict.iteritems():
        if key in ['_internal', '__builtins__']:
            continue
        if type(data) in [types.ModuleType, types.FunctionType, types.TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, types.ClassType, file]:
            continue
        result_dict[key] = safe_json(data)
    return result_dict

def safe_json(the_object, level=0):
    if level > 20:
        return None
    if type(the_object) in [str, unicode, bool, int, float]:
        return the_object
    if type(the_object) is list:
        return [safe_json(x, level=level+1) for x in the_object]
    if type(the_object) is dict:
        new_dict = dict()
        for key, value in the_object.iteritems():
            new_dict[key] = safe_json(value, level=level+1)
        return new_dict
    if type(the_object) is set:
        new_list = list()
        for sub_object in the_object:
            new_list.append(safe_json(sub_object, level=level+1))
        return new_list
    if type(the_object) in [types.ModuleType, types.FunctionType, types.TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, types.ClassType, file]:
        return None
    if isinstance(the_object, datetime.datetime):
        serial = the_object.isoformat()
        return serial
    if isinstance(the_object, datetime.time):
        serial = the_object.isoformat()
        return serial
    if isinstance(the_object, decimal.Decimal):
        return float(the_object)
    from docassemble.base.core import DAObject
    if isinstance(the_object, DAObject):
        new_dict = dict()
        new_dict['_class'] = type_name(the_object)
        for key, data in the_object.__dict__.iteritems():
            if key in ['has_nonrandom_instance_name', 'attrList']:
                continue
            new_dict[key] = safe_json(data, level=level+1)
        return new_dict
    try:
        json.dumps(the_object)
    except:
        return None
    return the_object

def referring_url(default=None):
    """Returns the URL that the user was visiting when the user clicked on
    a link to go to the interview."""
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

def plain(text, default=None):
    """Substitutes empty string or the value of the default parameter if the text is empty."""
    if text is None or text == '':
        if default is None:
            return ''
        else:
            return default
    return text

def bold(text, default=None):
    """Adds Markdown tags to make the text bold if it is not blank."""
    if text is None or text == '':
        if default is None:
            return ''
        else:
            return u'**' + unicode(default) + u'**'
    return u'**' + unicode(text) + u'**'

def italic(text, default=None):
    """Adds Markdown tags to make the text italic if it is not blank."""
    if text is None or text == '':
        if default is None:
            return ''
        else:
            return u'_' + unicode(default) + u'_'
    return u'_' + unicode(text) + u'_'

# def inspector():
#     frame = inspect.stack()[1][0]
#     for key in frame.__dict__.keys():
#         sys.stderr.write(str(key) + "\n")

def indent(text, by=None):
    """Indents multi-line text by four spaces.  To indent by a different
    amount, use the optional keyword argument 'by' to specify a
    different number of spaces.

    """
    if by is None:
        by = 4
    text = " " * 4 + unicode(text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n', '\n' + (" " * by), text)
    return text

def yesno(value, invert=False):
    """Returns 'Yes' or 'No' depending on whether the given value is true.
    This is used for populating PDF checkboxes.

    """
    if value is None or value == '' or value.__class__.__name__ == 'DAEmpty':
        return ""
    if value:
        if invert:
            return "No"
        return this_thread.misc.get('checkbox_export_value', 'Yes')
    if invert:
        return this_thread.misc.get('checkbox_export_value', 'Yes')
    return "No"

def noyes(value, invert=False):
    """Returns 'No' or 'Yes' depending on whether the given value is true
    or false, respectively.  This is used for populating PDF
    checkboxes.

    """
    if value is None or value == '' or value.__class__.__name__ == 'DAEmpty':
        return ""
    if value:
        if invert:
            return this_thread.misc.get('checkbox_export_value', 'Yes')
        return "No"
    if invert:
        return "No"
    return this_thread.misc.get('checkbox_export_value', 'Yes')

def split(text, breaks, index):
    """Splits text at particular breakpoints and returns the given piece."""
    text = re.sub(r'[\n\r]+', "\n", unicode(text).strip())
    if type(breaks) is not list:
        breaks = [breaks]
    lastbreakpoint = 0
    newbreaks = list()
    for breakpoint in breaks:
        newbreaks.append(breakpoint + lastbreakpoint)
        lastbreakpoint = breakpoint
    breaks = newbreaks
    if len(breaks) == 0:
        breaks = [0]
    elif breaks[0] != 0:
        breaks = [0] + breaks
    breaks = breaks + [float("inf")]
    parts = list()
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

def showif(var, condition):
    """Returns the variable indicated by the variable name if the
    condition is true, but otherwise returns empty text.

    """
    if condition:
        return value(var)
    return ''

def showifdef(var):
    """Returns the variable indicated by the variable name if it is
    defined, but otherwise returns empty text.

    """
    if defined(var):
        return value(var)
    return ''

def log(message, priority='log'):
    """Log a message to the server or the browser."""
    if priority == 'log':
        logmessage(unicode(message))
    else:
        this_thread.message_log.append(dict(message=unicode(message), priority=priority))

def get_message_log():
    return this_thread.message_log

def encode_name(var):
    """Convert a variable name to base64-encoded form for inclusion in an HTML element."""
    return codecs.encode(var.encode('utf8'), 'base64').decode().replace('\n', '')

def decode_name(var):
    """Convert a base64-encoded variable name to plain text."""
    return(codecs.decode(var, 'base64').decode('utf8'))

def interview_list(exclude_invalid=True, action=None, filename=None, session=None, user_id=None):
    """Returns a list of interviews that users have started."""
    if this_thread.current_info['user']['is_authenticated']:
        if user_id == 'all':
            user_id = None
        elif user_id is None:
            user_id = this_thread.current_info['user']['the_user_id']
        elif type(user_id) is not int:
            raise DAError("interview_list: user_id must be integer or 'all'")
        if action not in (None, 'delete_all', 'delete'):
            raise DAError("interview_list: invalid action")
        if action == 'delete' and (filename is None or session is None):
            raise DAError("interview_list: a filename and session must be provided when delete is the action.")
        return server.user_interviews(user_id=user_id, secret=this_thread.current_info['secret'], exclude_invalid=exclude_invalid, action=action, filename=filename, session=session)
    return None

def interview_menu():
    """Returns the list of interviews that is offered at /list."""
    return server.interview_menu()

def get_user_list(include_inactive=False):
    """Returns a list of users on the system."""
    if this_thread.current_info['user']['is_authenticated']:
        return server.get_user_list(include_inactive=include_inactive)
    return None

def manage_privileges(*pargs):
    """Gets or sets information about privileges on the system."""
    if this_thread.current_info['user']['is_authenticated']:
        arglist = list(pargs)
        if len(arglist) == 0:
            command = 'list'
        else:
            command = arglist.pop(0)
        if command == 'list':
            return server.get_privileges_list()
        elif command == 'add':
            for priv in arglist:
                server.add_privilege(priv)
        elif command == 'remove':
            for priv in arglist:
                server.remove_privilege(priv)
        else:
            raise Exception("manage_privileges: invalid command")
    return None

def get_user_info(user_id=None, email=None):
    """Returns information about the given user, or the current user, if no user ID or e-mail is provided."""
    if this_thread.current_info['user']['is_authenticated']:
        if user_id is None and email is None:
            user_id = this_thread.current_info['user']['the_user_id']
        return server.get_user_info(user_id=user_id, email=email)
    return None

def set_user_info(**kwargs):
    """Sets information about the given user, or the current user, if no user ID or e-mail is provided"""
    user_id = kwargs.get('user_id', None)
    email = kwargs.get('email', None)
    server.set_user_info(**kwargs)
    if 'privileges' in kwargs and type(kwargs['privileges']) in (list, tuple) and len(kwargs['privileges']) > 0:
        this_thread.current_info['user']['roles'] = [y for y in kwargs['privileges']]
    if (user_id is None and email is None) or (user_id is not None and user_id == this_thread.current_info['user']['theid']) or (email is not None and email == this_thread.current_info['user']['email']):
        for key, val in kwargs.iteritems():
            if key in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
                this_thread.current_info['user'][key] = val

def get_user_secret(username, password):
    """Tests the username and password and if they are valid, returns the
    decryption key for the user account.

    """
    return server.get_secret(username, password)

def get_session_variables(yaml_filename, session_id, secret=None, simplify=True):
    """Returns the interview dictionary for the given interview session."""
    return server.get_session_variables(yaml_filename, session_id, secret=secret, simplify=True)

def set_session_variables(yaml_filename, session_id, variables, secret=None):
    """Sets variables in the interview dictionary for the given interview session."""
    if session_id == get_uid() and yaml_filename == this_thread.current_info.get('yaml_filename', None):
        raise Exception("You cannot set variables in the current interview session")
    server.set_session_variables(yaml_filename, session_id, dict(), secret=secret, literal_variables=variables)

def go_back_in_session(yaml_filename, session_id, secret=None):
    """Goes back one step in an interview session."""
    if session_id == get_uid() and yaml_filename == this_thread.current_info.get('yaml_filename', None):
        raise Exception("You cannot go back in the current interview session")
    server.go_back_in_session(yaml_filename, session_id, secret=secret)
