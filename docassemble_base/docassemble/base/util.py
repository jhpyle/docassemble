# -*- coding: utf-8 -*-
import datetime
import time
import pytz
import yaml
from PIL import Image, ImageEnhance
from twilio.rest import Client as TwilioRestClient
import pycountry
import docassemble.base.ocr
from celery import chord
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError
from docassemble.base.functions import alpha, roman, item_label, comma_and_list, get_language, set_language, get_dialect, set_country, get_country, word, comma_list, ordinal, ordinal_number, need, nice_number, quantity_noun, possessify, verb_past, verb_present, noun_plural, noun_singular, space_to_underscore, force_ask, force_gather, period_list, name_suffix, currency_symbol, currency, indefinite_article, nodoublequote, capitalize, title_case, url_of, do_you, did_you, does_a_b, did_a_b, were_you, was_a_b, have_you, has_a_b, your, her, his, is_word, get_locale, set_locale, process_action, url_action, get_info, set_info, get_config, prevent_going_back, qr_code, action_menu_item, from_b64_json, defined, value, message, response, json_response, command, single_paragraph, quote_paragraphs, location_returned, location_known, user_lat_lon, interview_url, interview_url_action, interview_url_as_qr, interview_url_action_as_qr, interview_email, get_emails, this_thread, static_image, action_arguments, action_argument, language_functions, language_function_constructor, get_default_timezone, user_logged_in, interface, user_privileges, user_has_privilege, user_info, task_performed, task_not_yet_performed, mark_task_as_performed, times_task_performed, set_task_counter, background_action, background_response, background_response_action, us, set_live_help_status, chat_partners_available, phone_number_in_e164, phone_number_is_valid, countries_list, country_name, write_record, read_records, delete_record, variables_as_json, all_variables, server, language_from_browser, device, plain, bold, italic, states_list, state_name, subdivision_type, indent, raw, fix_punctuation
from docassemble.base.core import DAObject, DAList, DADict, DASet, DAFile, DAFileCollection, DAFileList, DAEmail, DAEmailRecipient, DAEmailRecipientList, DATemplate, selections, objects_from_file
from decimal import Decimal
import sys
#sys.stderr.write("importing async mail now from util\n")
from docassemble.base.filter import markdown_to_html, to_text

#file_finder, url_finder, da_send_mail

import docassemble.base.filter
import dateutil
import dateutil.parser
import json
import codecs
import babel.dates
import redis
import re
import phonenumbers
import tempfile
import os
import shutil
import subprocess
from bs4 import BeautifulSoup

__all__ = ['alpha', 'roman', 'item_label', 'ordinal', 'ordinal_number', 'comma_list', 'word', 'get_language', 'set_language', 'get_dialect', 'set_country', 'get_country', 'get_locale', 'set_locale', 'comma_and_list', 'need', 'nice_number', 'quantity_noun', 'currency_symbol', 'verb_past', 'verb_present', 'noun_plural', 'noun_singular', 'indefinite_article', 'capitalize', 'space_to_underscore', 'force_ask', 'force_gather', 'period_list', 'name_suffix', 'currency', 'static_image', 'title_case', 'url_of', 'process_action', 'url_action', 'get_info', 'set_info', 'get_config', 'prevent_going_back', 'qr_code', 'action_menu_item', 'from_b64_json', 'defined', 'value', 'message', 'response', 'json_response', 'command', 'single_paragraph', 'quote_paragraphs', 'location_returned', 'location_known', 'user_lat_lon', 'interview_url', 'interview_url_action', 'interview_url_as_qr', 'interview_url_action_as_qr', 'LatitudeLongitude', 'RoleChangeTracker', 'Name', 'IndividualName', 'Address', 'City', 'Event', 'Person', 'Thing', 'Individual', 'ChildList', 'FinancialList', 'PeriodicFinancialList', 'Income', 'Asset', 'Expense', 'Value', 'PeriodicValue', 'OfficeList', 'Organization', 'objects_from_file', 'send_email', 'send_sms', 'map_of', 'selections', 'DAObject', 'DAList', 'DADict', 'DASet', 'DAFile', 'DAFileCollection', 'DAFileList', 'DAEmail', 'DAEmailRecipient', 'DAEmailRecipientList', 'DATemplate', 'last_access_time', 'last_access_delta', 'last_access_days', 'last_access_hours', 'last_access_minutes', 'action_arguments', 'action_argument', 'timezone_list', 'as_datetime', 'current_datetime', 'date_difference', 'date_interval', 'year_of', 'month_of', 'day_of', 'format_date', 'format_time', 'today', 'get_default_timezone', 'user_logged_in', 'interface', 'user_privileges', 'user_has_privilege', 'user_info', 'task_performed', 'task_not_yet_performed', 'mark_task_as_performed', 'times_task_performed', 'set_task_counter', 'background_action', 'background_response', 'background_response_action', 'us', 'DARedis', 'MachineLearningEntry', 'SimpleTextMachineLearner', 'SVMMachineLearner', 'set_live_help_status', 'chat_partners_available', 'phone_number_in_e164', 'phone_number_is_valid', 'countries_list', 'country_name', 'write_record', 'read_records', 'delete_record', 'variables_as_json', 'all_variables', 'ocr_file', 'ocr_file_in_background', 'get_sms_session', 'initiate_sms_session', 'terminate_sms_session', 'language_from_browser', 'device', 'interview_email', 'get_emails', 'plain', 'bold', 'italic', 'path_and_mimetype', 'states_list', 'state_name', 'subdivision_type', 'indent', 'raw', 'fix_punctuation']

#knn_machine_learner = DummyObject

# def TheSimpleTextMachineLearner(*pargs, **kwargs):
#     return knn_machine_learner(*pargs, **kwargs)

redis_server = None

def redis_server():
    return re.sub(r'^redis://', r'', server.redis_host)

class DARedis(DAObject):
    """A class used to interact with the redis server."""
    def key(self, keyname):
        """Returns a key that combines the interview name with the keyname."""
        return this_thread.current_info.get('yaml_filename', '') + ':' + str(keyname)
    def __getattr__(self, funcname):
        if this_thread.redis is None:
            this_thread.redis = redis.StrictRedis(host=redis_server, db=2)
        return getattr(this_thread.redis, funcname)

def set_redis_server(redis_host):
    global redis_server
    redis_server = re.sub(r'^redis://', r'', redis_host)

# def default_user_id_function():
#     return dict()

# user_id_dict = default_user_id_function

# def set_user_id_function(func):
#     global user_id_dict
#     user_id_dict = func
#     return

def today_default(format='long', timezone=None):
    if timezone is None:
        timezone = get_default_timezone()
    return babel.dates.format_date(pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(timezone)).date(), format=format, locale=this_thread.language)

language_functions['today'] = {'*': today_default}

today = language_function_constructor('today')
if today.__doc__ is None:
    today.__doc__ = """Returns today's date in long form according to the current locale."""    

def month_of(the_date, as_word=False):
    """Interprets the_date as a date and returns the month.  
    Set as_word to True if you want the month as a word."""
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        if as_word:
            return(date.strftime('%B'))
        return(date.strftime('%m'))
    except:
        return word("Bad date")

def day_of(the_date):
    """Interprets the_date as a date and returns the day of month."""
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return(date.strftime('%d'))
    except:
        return word("Bad date")

def year_of(the_date):
    """Interprets the_date as a date and returns the year."""
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return(date.strftime('%Y'))
    except:
        return word("Bad date")

def format_date(the_date, format='long'):
    """Interprets the_date as a date and returns the date formatted for the current locale."""
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return babel.dates.format_date(date, format=format, locale=get_language())
    except:
        return word("Bad date")

def format_time(the_time, format='short'):
    """Interprets the_time as a date/time and returns the time formatted for the current locale."""
    try:
        if isinstance(the_time, datetime.datetime) or isinstance(the_time, datetime.date):
            time = the_time
        else:
            time = dateutil.parser.parse(the_time)
        return babel.dates.format_time(time, format=format, locale=get_language())
    except Exception as errmess:
        return word("Bad date: " + str(errmess))

class DateTimeDelta(object):
    def __str__(self):
        return quantity_noun(output.days, word('day'))
    pass

def current_datetime(timezone=None):
    """Returns the current time as a datetime.datetime object with a timezone.
    Uses the default timezone unless another timezone is explicitly provided."""
    if timezone is None:
        timezone = get_default_timezone()
    return pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(timezone))

def as_datetime(the_date, timezone=None):
    """Converts the_date to a datetime.datetime object with a timezone.  Uses the
    default timezone unless another timezone is explicitly provided."""
    if timezone is None:
        timezone = get_default_timezone()
    if isinstance(the_date, datetime.date):
        the_date = datetime.datetime.combine(the_date, datetime.datetime.min.time())
    if isinstance(the_date, datetime.datetime):
        new_datetime = the_date
    else:
        new_datetime = dateutil.parser.parse(the_date)
    if new_datetime.tzinfo:
        new_datetime = new_datetime.astimezone(pytz.timezone(timezone))
    else:
        new_datetime = pytz.timezone(timezone).localize(new_datetime)
    return new_datetime

def date_interval(**kwargs):
    """Expresses a date and time interval.  Passes through all arguments 
    to dateutil.relativedelta.relativedelta."""
    return dateutil.relativedelta.relativedelta(**kwargs)

def date_difference(starting=current_datetime(), ending=current_datetime(), timezone=None):
    """Calculates the difference between the date indicated by "starting" 
    and the date indicated by "ending."  Returns an object with attributes weeks, 
    days, hours, minutes, seconds, and delta."""
    if timezone is None:
        timezone = get_default_timezone()
    if isinstance(starting, datetime.date):
        starting = datetime.datetime.combine(starting, datetime.datetime.min.time())
    if isinstance(ending, datetime.date):
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
    output.weeks = (delta.days / 7.0) + (delta.seconds / 604800.0)
    output.days = delta.days + (delta.seconds / 86400.0)
    output.hours = (delta.days * 24.0) + (delta.seconds / 3600.0)
    output.minutes = (delta.days * 1440.0) + (delta.seconds / 60.0)
    output.seconds = (delta.days * 86400) + delta.seconds
    output.years = (delta.days + delta.seconds / 86400.0) / 365.2425
    return output

def phone_string(person):
    if person is None:
        return None
    phone_number = None
    if isinstance(person, Person):
        phone_number = person.sms_number()
    elif isinstance(person, phonenumbers.PhoneNumber):
        phone_number = phonenumbers.format_number(person, phonenumbers.PhoneNumberFormat.E164)
    else:
        phone_number = phone_number_in_e164(person)
    return phone_number

def email_string(persons, include_name=None, first=False):
    if persons is None:
        return None
    if not hasattr(persons, '__iter__'):
        persons = [persons]
    result = []
    for person in persons:
        if isinstance(person, Person) or isinstance(person, DAEmailRecipient):
            result.append(person.email_address(include_name=include_name))
        else:
            result.append(str(person))
    result = [x for x in result if x is not None and x != '']
    if len(result) and first:
        return [result[0]]
    return result

def email_stringer(variable, first=False):
    return email_string(variable, include_name=False, first=first)

def valid_datetime(the_datetime):
    """Returns True if the provided text represents a valid date or time."""
    if isinstance(the_datetime, datetime.datetime) or isinstance(the_datetime, datetime.date):
        return True
    try:
        dateutil.parser.parse(the_datetime)
        return True
    except:
        return False

def timezone_list():
    """Returns a list of timezone choices, expressed as text."""
    return sorted([tz for tz in pytz.all_timezones])

def last_access_delta(*pargs, **kwargs):
    """Returns a datatime.timedelta object expressing the length of
    time that has passed since the last time the interview was accessed."""
    last_time = last_access_time(*pargs, **kwargs)
    if last_time is None:
        return datetime.timedelta(0)
    return datetime.datetime.utcnow() - last_time

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

def last_access_time(*pargs, **kwargs):
    """Returns the last time the interview was accessed, as a 
    datetime.datetime object."""
    include_cron = kwargs.get('include_cron', False)
    max_time = None
    roles = None
    if len(pargs) > 0:
        roles = pargs[0]
        if type(roles) is not list:
            roles = [roles]
        if 'cron' in roles:
            include_cron = True    
    lookup_dict = server.user_id_dict()
    for user_id, access_time in this_thread.internal['accesstime'].iteritems():
        if user_id in lookup_dict and hasattr(lookup_dict[user_id], 'roles'):
            for role in lookup_dict[user_id].roles:
                if include_cron is False:
                    if role.name == 'cron':
                        continue
                if roles is None or role in roles:
                    if max_time is None or max_time < access_time:
                        max_time = access_time
    return max_time

class LatitudeLongitude(DAObject):
    """Represents a GPS location."""
    def init(self, *pargs, **kwargs):
        self.gathered = False
        self.known = False
        self.description = ""
        return super(LatitudeLongitude, self).init(*pargs, **kwargs)
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
        if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and type(this_thread.current_info['user']['location']) is dict:
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
        #logmessage("Current role is " + str(this_thread.role))
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
    def firstlast(self):
        """This method is included for compatibility with other types of names."""
        return(self.text)
    def lastfirst(self):
        """This method is included for compatibility with other types of names."""
        return(self.text)
    def defined(self):
        """Returns True if the name has been defined.  Otherwise, returns False."""
        return hasattr(self, 'text')
    def __str__(self):
        return(self.full())
#    def __repr__(self):
#        return(repr(self.full()))

class IndividualName(Name):
    """The name of an Individual."""
    def init(self, *pargs, **kwargs):
        if 'uses_parts' not in kwargs:
            self.uses_parts = True
        return super(IndividualName, self).init(*pargs, **kwargs)
    def defined(self):
        """Returns True if the name has been defined.  Otherwise, returns False."""
        if not self.uses_parts:
            return super(IndividualName, self).defined()
        return hasattr(self, 'first')
    def full(self, middle='initial', use_suffix=True):
        """Returns the full name.  Has optional keyword arguments middle 
        and use_suffix."""
        if not self.uses_parts:
            return super(IndividualName, self).full()
        names = [self.first]
        if hasattr(self, 'middle') and len(self.middle):
            if middle is False or middle is None:
                pass
            elif middle == 'initial':
                names.append(self.middle[0] + '.')
            else:
                names.append(self.middle)
        if hasattr(self, 'last') and len(self.last):
            names.append(self.last)
        if hasattr(self, 'suffix') and use_suffix and len(self.suffix):
            names.append(self.suffix)
        return(" ".join(names))
    def firstlast(self):
        """Returns the first name followed by the last name."""
        if not self.uses_parts:
            return super(IndividualName, self).firstlast()
        return(self.first + " " + self.last)
    def lastfirst(self):
        """Returns the last name followed by a comma, followed by the 
        last name, followed by the suffix (if a suffix exists)."""
        if not self.uses_parts:
            return super(IndividualName, self).lastfirst()
        output = self.last
        if hasattr(self, 'suffix') and self.suffix:
            output += " " + self.suffix
        output += ", " + self.first
        if hasattr(self, 'middle') and self.middle:
            output += " " + self.middle[0] + '.'
        return output

class Address(DAObject):
    """A geographic address."""
    def init(self, *pargs, **kwargs):
        if 'location' not in kwargs:
            self.location = LatitudeLongitude()
        if 'geolocated' not in kwargs:
            self.geolocated = False
        if not hasattr(self, 'city_only'):
            self.city_only = False
        return super(Address, self).init(*pargs, **kwargs)
    def __str__(self):
        return(self.block())
    def on_one_line(self, include_unit=False, omit_default_country=True):
        """Returns a one-line address.  Primarily used internally for geolocation."""
        output = ""
        if self.city_only is False:
            output += str(self.address)
            if include_unit and hasattr(self, 'unit') and self.unit != '' and self.unit is not None:
                output += ", " + str(self.unit)
            output += ", "
        output += str(self.city) + ", " + str(self.state)
        if hasattr(self, 'zip') and self.zip:
            output += " " + str(self.zip)
        if hasattr(self, 'country') and self.country:
            if (not omit_default_country) or get_country() != self.country:
                output += ", " + country_name(self.country)
        return output
    def _map_info(self):
        if (self.location.gathered and self.location.known) or self.address.geolocate():
            the_info = self.location.description
            result = {'latitude': self.location.latitude, 'longitude': self.location.longitude, 'info': the_info}
            if hasattr(self, 'icon'):
                result['icon'] = self.icon
            return [result]
        return None
    def geolocate(self):
        """Determines the latitude and longitude of the location."""
        if self.geolocated:
            return self.geolocate_success    
        the_address = self.on_one_line(omit_default_country=False)
        #logmessage("geolocate: trying to geolocate " + str(the_address))
        from geopy.geocoders import GoogleV3        
        if 'google' in server.daconfig and 'api key' in server.daconfig['google'] and server.daconfig['google']['api key']:
            my_geocoder = GoogleV3(api_key=server.daconfig['google']['api key'])
        else:
            my_geocoder = GoogleV3()
        try_number = 0
        success = False
        results = None
        while not success and try_number < 2:
            try:
                results = my_geocoder.geocode(the_address)
                success = True
            except:
                try_number += 1
                time.sleep(try_number)
        self.geolocated = True
        if results:
            self.geolocate_success = True
            self.location.gathered = True
            self.location.known = True
            self.location.latitude = results.latitude
            self.location.longitude = results.longitude
            self.location.description = self.block()
            self.geolocate_response = results.raw
            if 'address_components' in results.raw:
                geo_types = {'administrative_area_level_2': 'county', 'neighborhood': 'neighborhood', 'postal_code': 'zip', 'country': 'country'}
                for component in results.raw['address_components']:
                    if 'types' in component and 'long_name' in component:
                        for geo_type, addr_type in geo_types.iteritems():
                            if geo_type in component['types'] and ((not hasattr(self, addr_type)) or getattr(self, addr_type) == '' or getattr(self, addr_type) is None):
                                #logmessage("Setting " + str(addr_type) + " to " + str(getattr(results[0], geo_type)) + " from " + str(geo_type))
                                setattr(self, addr_type, component['long_name'])
        else:
            logmessage("geolocate: Valid not ok.")
            self.geolocate_success = False
        #logmessage(str(self.__dict__))
        return self.geolocate_success
    def block(self):
        """Returns the address formatted as a block, as in a mailing."""
        output = ""
        if this_thread.evaluation_context == 'docx':
            line_breaker = "\n"
        else:
            line_breaker = " [NEWLINE] "
        if self.city_only is False:
            output += str(self.address) + line_breaker
            if hasattr(self, 'unit') and self.unit != '' and self.unit is not None:
                output += str(self.unit) + line_breaker
        output += str(self.city) + ", " + str(self.state)
        if hasattr(self, 'zip'):
            output += " " + str(self.zip)
        return(output)
    def line_one(self):
        """Returns the first line of the address, including the unit 
        number if there is one."""
        if self.city_only:
            return ''
        output = str(self.address)
        if hasattr(self, 'unit') and self.unit != '' and self.unit is not None:
            output += ", " + str(self.unit)
        return(output)
    def line_two(self):
        """Returns the second line of the address, including the city,
        state and zip code."""
        output = str(self.city) + ", " + str(self.state) + " " + str(self.zip)
        return(output)

class City(Address):
    """A geographic address specific only to a city."""
    def init(self, *pargs, **kwargs):
        self.city_only = True
        return super(City, self).init(*pargs, **kwargs)

class Thing(DAObject):
    """Represents something with a name."""
    def init(self, *pargs, **kwargs):
        if not hasattr(self, 'name') and 'name' not in kwargs:
            self.name = Name()
        if 'name' in kwargs and type(kwargs['name']) in (str, unicode):
            if not hasattr(self, 'name'):
                self.name = Name()
            self.name.text = kwargs['name']
            del kwargs['name']
        return super(Thing, self).init(*pargs, **kwargs)
    def __str__(self):
        return self.name.full()

class Event(DAObject):
    def init(self, *pargs, **kwargs):
        if 'address' not in kwargs:
            self.address = City()
        if 'location' not in kwargs:
            self.location = LatitudeLongitude()
        return super(Event, self).init(*pargs, **kwargs)
    def __str__(self):
        return str(self.address)
    
class Person(DAObject):
    """Represents a legal or natural person."""
    def init(self, *pargs, **kwargs):
        if not hasattr(self, 'name') and 'name' not in kwargs:
            self.name = Name()
        if 'address' not in kwargs:
            self.address = Address()
        if 'location' not in kwargs:
            self.location = LatitudeLongitude()
        if 'name' in kwargs and type(kwargs['name']) in (str, unicode):
            if not hasattr(self, 'name'):
                self.name = Name()
            self.name.text = kwargs['name']
            del kwargs['name']
        if 'roles' not in kwargs:
            self.roles = set()
        return super(Person, self).init(*pargs, **kwargs)
    def _map_info(self):
        if not self.location.known:
            if (self.address.location.gathered and self.address.location.known) or self.address.geolocate():
                self.location = self.address.location
        if self.location.gathered and self.location.known:
            if self.name.defined():
                the_info = self.name.full()
            else:
                the_info = capitalize(self.object_name())
            the_info += " [NEWLINE] " + self.location.description
            result = {'latitude': self.location.latitude, 'longitude': self.location.longitude, 'info': the_info}
            if hasattr(self, 'icon'):
                result['icon'] = self.icon
            elif self is this_thread.user:
                result['icon'] = {'path': 'CIRCLE', 'scale': 5, 'strokeColor': 'blue'}
            return [result]
        return None
    def identified(self):
        """Returns True if the person's name has been set.  Otherwise, returns False."""
        if hasattr(self.name, 'text'):
            return True
        return False
    def __setattr__(self, attrname, value):
        if attrname == 'name' and type(value) in [str, unicode]:
            self.name.text = value
        else:
            return super(Person, self).__setattr__(attrname, value)
    def __str__(self):
        return self.name.full()
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
        if self is this_thread.user:
            return your(target, **kwargs)
        else:
            return possessify(self.name, target)
    def object_possessive(self, target, **kwargs):
        """Given a word, returns a phrase indicating possession, but
        uses the variable name rather than the object's actual name."""
        if self is this_thread.user:
            return your(target, **kwargs)
        return super(Person, self).object_possessive(target, **kwargs)
    def is_are_you(self, **kwargs):
        """Returns "are you" if the object is the user, otherwise returns
        "is" followed by the object name."""
        if self is this_thread.user:
            output = word('are you', **kwargs)
        else:
            output = is_word(self.name.full(), **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def is_user(self):
        """Returns True if the person is the user, otherwise False."""
        return self is this_thread.user
    def address_block(self):
        """Returns the person name address as a block, for use in mailings."""
        if this_thread.evaluation_context == 'docx':
            return(self.name.full() + "\n" + self.address.block())
        else:
            return("[FLUSHLEFT] " + self.name.full() + " [NEWLINE] " + self.address.block())
    def sms_number(self):
        """Returns the person's mobile_number, if defined, otherwise the phone_number."""
        if hasattr(self, 'mobile_number'):
            the_number = self.mobile_number
        else:
            the_number = self.phone_number
        if hasattr(self, 'country'):
            the_country = self.country
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
        if self == this_thread.user:
            return(do_you(the_verb, **kwargs))
        else:
            return(does_a_b(self.name, the_verb, **kwargs))
    def did_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "did you eat" or "did John Smith eat,"
        depending on whether the person is the user."""
        if self == this_thread.user:
            return(did_you(the_verb, **kwargs))
        else:
            return(did_a_b(self.name, the_verb, **kwargs))
    def were_question(self, the_target, **kwargs):
        """Given a target like "married", returns "were you married" or "was
        John Smith married," depending on whether the person is the
        user."""
        if self == this_thread.user:
            return(were_you(the_target, **kwargs))
        else:
            return(was_a_b(self.name, the_target, **kwargs))
    def have_question(self, the_target, **kwargs):
        """Given a target like "", returns "have you married" or "has
        John Smith married," depending on whether the person is the
        user."""
        if self == this_thread.user:
            return(have_you(the_target, **kwargs))
        else:
            return(has_a_b(self.name, the_target, **kwargs))
    def does_verb(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "eat" or "eats"
        depending on whether the person is the user."""
        if self == this_thread.user:
            tense = '1sg'
        else:
            tense = '3sg'
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            return verb_past(the_verb, tense)
        else:
            return verb_present(the_verb, tense)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except uses the past tense of the verb."""
        if self == this_thread.user:
            tense = "2sgp"
        else:
            tense = "3sgp"
        #logmessage(the_verb + " " + tense)
        return verb_past(the_verb, tense)
    def subject(self, **kwargs):
        """Returns "you" or the person's name, depending on whether the 
        person is the user."""
        if self == this_thread.user:
            output = 'you'
        else:
            output = str(self)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)

class Individual(Person):
    """Represents a natural person."""
    def init(self, *pargs, **kwargs):
        if 'name' not in kwargs:
            self.name = IndividualName()
        if 'child' not in kwargs:
            self.child = ChildList()
        if 'income' not in kwargs:
            self.income = Income()
        if 'asset' not in kwargs:
            self.asset = Asset()
        if 'expense' not in kwargs:
            self.expense = Expense()
        return super(Individual, self).init(*pargs, **kwargs)
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
            comparator = datetime.datetime.utcnow()
        else:
            comparator = dateutil.parser.parse(as_of)
        rd = dateutil.relativedelta.relativedelta(comparator, dateutil.parser.parse(self.birthdate))
        if decimals:
            return float(rd.years)
        else:
            return int(rd.years)
    def first_name_hint(self):
        """If the individual is the user and the user is logged in and 
        the user has set up a name in the user profile, this returns 
        the user's first name.  Otherwise, returns a blank string."""
        if self is this_thread.user and this_thread.current_info['user']['is_authenticated'] and 'firstname' in this_thread.current_info['user'] and this_thread.current_info['user']['firstname']:
            return this_thread.current_info['user']['firstname'];
        return ''
    def last_name_hint(self):
        """If the individual is the user and the user is logged in and 
        the user has set up a name in the user profile, this returns 
        the user's last name.  Otherwise, returns a blank string."""
        if self is this_thread.user and this_thread.current_info['user']['is_authenticated'] and 'lastname' in this_thread.current_info['user'] and this_thread.current_info['user']['lastname']:
            return this_thread.current_info['user']['lastname'];
        return ''
    def salutation(self):
        """Depending on the gender attribute, returns "Mr." or "Ms." """
        if self.gender == 'female':
            return('Ms.')
        else:
            return('Mr.')
    def pronoun_possessive(self, target, **kwargs):
        """Given a word like "fish," returns "her fish" or "his fish," as appropriate."""
        if self == this_thread.user and ('thirdperson' not in kwargs or not kwargs['thirdperson']):
            output = your(target, **kwargs)
        elif self.gender == 'female':
            output = her(target, **kwargs)
        else:
            output = his(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        """Returns a pronoun like "you," "her," or "him," as appropriate."""
        if self == this_thread.user:
            output = word('you', **kwargs)
        if self.gender == 'female':
            output = word('her', **kwargs)
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
        if self == this_thread.user and ('thirdperson' not in kwargs or not kwargs['thirdperson']):
            output = word('you', **kwargs)
        elif self.gender == 'female':
            output = word('she', **kwargs)
        else:
            output = word('he', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def yourself_or_name(self, **kwargs):
        """Returns a "yourself" if the individual is the user, otherwise 
        returns the individual's name."""
        if self == this_thread.user:
            output = word('yourself', **kwargs)
        else:
            output = self.name.full()
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)

class ChildList(DAList):
    """Represents a list of children."""
    def init(self, *pargs, **kwargs):
        self.object_type = Individual
        return super(ChildList, self).init(*pargs, **kwargs)

class FinancialList(DADict):
    """Represents a set of currency amounts."""
    def init(self, *pargs, **kwargs):
        self.object_type = Value
        return super(FinancialList, self).init(*pargs, **kwargs)
    def total(self):
        """Returns the total value in the list, gathering the list items if necessary."""
        self._trigger_gather()
        result = 0
        for item in self.elements:
            if self[item].exists:
                result += Decimal(self[item].value)
        return(result)
    def existing_items(self):
        """Returns a list of types of amounts that exist within the financial list."""
        self._trigger_gather()
        return [key for key in self.elements if self[key].exists]
    def _new_item_init_callback(self):
        self.elements[self.new_item_name].exists = True
        if hasattr(self, 'new_item_value'):
            self.elements[self.new_item_name].value = self.new_item_value
            del self.new_item_value
        return super(FinancialList, self)._new_item_init_callback()
    def __str__(self):
        return str(self.total())
    
class PeriodicFinancialList(FinancialList):
    """Represents a set of currency items, each of which has an associated period."""
    def init(self, *pargs, **kwargs):
        self.object_type = PeriodicValue
        return super(FinancialList, self).init(*pargs, **kwargs)
    def total(self, period_to_use=1):
        """Returns the total periodic value in the list, gathering the list items if necessary."""
        self._trigger_gather()
        result = 0
        if period_to_use == 0:
            return(result)
        for item in self.elements:
            if self.elements[item].exists:
                result += Decimal(self.elements[item].value) * Decimal(self.elements[item].period)
        return(result/Decimal(period_to_use))
    def _new_item_init_callback(self):
        if hasattr(self, 'new_item_period'):
            self.elements[self.new_item_name].period = self.new_item_period
            del self.new_item_period
        return super(PeriodicFinancialList, self)._new_item_init_callback()

class Income(PeriodicFinancialList):
    """A PeriodicFinancialList representing a person's income."""
    pass

class Asset(FinancialList):
    """A FinancialList representing a person's assets."""
    pass

class Expense(PeriodicFinancialList):
    """A PeriodicFinancialList representing a person's expenses."""
    pass

class Value(DAObject):
    """Represents a value in a FinancialList."""
    def amount(self):
        """Returns the value's amount, or 0 if the value does not exist."""
        if not self.exists:
            return 0
        return (Decimal(self.value))
    def __str__(self):
        return str(self.amount())

class PeriodicValue(Value):
    """Represents a value in a PeriodicFinancialList."""
    def amount(self, period_to_use=1):
        """Returns the periodic value's amount for a full period, 
        or 0 if the value does not exist."""
        if not self.exists:
            return 0
        #logmessage("period is a " + str(type(self.period).__name__))
        return (Decimal(self.value) * Decimal(self.period)) / Decimal(period_to_use)

class OfficeList(DAList):
    """Represents a list of offices of a company or organization."""
    def init(self, *pargs, **kwargs):
        self.object_type = Address
        return super(OfficeList, self).init(*pargs, **kwargs)

class Organization(Person):
    """Represents a company or organization."""
    def init(self, *pargs, **kwargs):
        self.initializeAttribute('office', OfficeList)
        if 'offices' in kwargs:
            if type(kwargs['offices']) is list:
                for office in kwargs['offices']:
                    if type(office) is dict:
                        new_office = self.office.appendObject(Address, **office)
                        new_office.geolocate()
            del kwargs['offices']
        return super(Organization, self).init(*pargs, **kwargs)
    def will_handle(self, problem=None, county=None):
        """Returns True or False depending on whether the organization 
        serves the given county and/or handles the given problem."""
        #logmessage("Testing " + str(problem) + " against " + str(self.handles))
        if problem:
            if not (hasattr(self, 'handles') and problem in self.handles):
                return False
        if county:
            if not (hasattr(self, 'serves') and county in self.serves):
                return False
        return True
    def _map_info(self):
        the_response = list()
        for office in self.office:
            if (office.location.gathered and office.location.known) or office.geolocate():
                if self.name.defined():
                    the_info = self.name.full()
                else:
                    the_info = capitalize(self.object_name())
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

def send_sms(to=None, body=None, template=None, task=None, attachments=None, config='default'):
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
            body_html += markdown_to_html(template.subject)
        body_html += markdown_to_html(template.content) + '</body></html>'
        body = BeautifulSoup(body_html, "html.parser").get_text('\n')
    if body is None:
        body = word("blank message")
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
    success = True
    media = list()
    for attachment in attachments:
        attachment_list = list()
        if type(attachment) is DAFileCollection:
            subattachment = getattr(attachment, 'pdf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'rtf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'tex', None)
            if subattachment is not None:
                attachment_list.append(subattachment)
            else:
                logmessage("send_sms: could not find file to attach in DAFileCollection.")
                success = False
        elif type(attachment) is DAFile:
            attachment_list.append(attachment)
        elif type(attachment) is DAFileList:
            attachment_list.extend(attachment.elements)
        elif type(attachment) in [str, unicode] and re.search(r'^https?://', attachment):
            attachment_list.append(attachment)
        else:
            logmessage("send_sms: attachment " + str(attachment) + " is not valid.")
            success = False
        if success:
            for the_attachment in attachment_list:
                if type(the_attachment) is DAFile and the_attachment.ok:
                    url = url_start + docassemble.base.filter.url_for('serve_stored_file', uid=this_thread.current_info['session'], number=the_attachment.number, filename=the_attachment.filename, extension=the_attachment.extension)
                    media.append(url)
                elif type(the_attachment) in [str, unicode]:
                    media.append(the_attachment)
    if len(media) > 10:
        logmessage("send_sms: more than 10 attachments were provided; not sending message")
        success = False
    if success:
        twilio_client = TwilioRestClient(tconfig['account sid'], tconfig['auth token'])
        for recipient in to:
            phone_number = phone_string(recipient)
            if phone_number is not None:
                try:
                    if len(media):
                        message = twilio_client.messages.create(to=phone_number, from_=tconfig['number'], body=body, media_url=media)
                    else:
                        message = twilio_client.messages.create(to=phone_number, from_=tconfig['number'], body=body)
                except Exception as errstr:
                    logmessage("send_sms: failed to send message: " + str(errstr))
                    return False
    if success and task is not None:
        mark_task_as_performed(task)
    return True

def send_email(to=None, sender=None, cc=None, bcc=None, body=None, html=None, subject="", template=None, task=None, attachments=None):
    """Sends an e-mail and returns whether sending the e-mail was successful."""
    if attachments is None:
        attachments = []
    from flask_mail import Message
    if type(to) is not list:
        to = [to]
    if len(to) == 0:
        return False
    if template is not None:
        if subject is None or subject == '':
            subject = template.subject
        body_html = '<html><body>' + markdown_to_html(template.content) + '</body></html>'
        if body is None:
            body = BeautifulSoup(body_html, "html.parser").get_text('\n')
        if html is None:
            html = body_html
    if body is None and html is None:
        body = ""
    msg = Message(subject, sender=email_stringer(sender, first=True), recipients=email_stringer(to), cc=email_stringer(cc), bcc=email_stringer(bcc), body=body, html=html)
    filenames_used = set()
    success = True
    for attachment in attachments:
        attachment_list = list()
        if type(attachment) is DAFileCollection:
            subattachment = getattr(attachment, 'pdf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'rtf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'tex', None)
            if subattachment is not None:
                attachment_list.append(subattachment)
            else:
                success = False
        elif type(attachment) is DAFile:
            attachment_list.append(attachment)
        elif type(attachment) is DAFileList:
            attachment_list.extend(attachment.elements)
        elif type(attachment) in (str, unicode):
            file_info = server.file_finder(attachment)
            if 'fullpath' in file_info:
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
                if the_attachment.ok:
                    file_info = server.file_finder(str(the_attachment.number))
                    if 'fullpath' in file_info:
                        failed = True
                        with open(file_info['fullpath'], 'rb') as fp:
                            msg.attach(attachment_name(the_attachment.filename, filenames_used), file_info['mimetype'], fp.read())
                            failed = False
                        if failed:
                            success = False
                    else:
                        success = False
    if success:
        try:
            logmessage("send_email: starting to send")
            server.send_mail(msg)
            logmessage("send_email: finished sending")
        except Exception as errmess:
            logmessage("send_email: sending mail failed: " + str(errmess))
            success = False
    if success and task is not None:
        mark_task_as_performed(task)
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
        if type(arg) is list:
            all_args.extend(arg)
        else:
            all_args.append(arg)
    for arg in all_args:
        if isinstance(arg, DAObject):
            markers = arg._map_info()
            if markers:
                for marker in markers:
                    if 'icon' in marker and type(marker['icon']) is not dict:
                        marker['icon'] = {'url': server.url_finder(marker['icon'])}
                    if 'info' in marker and marker['info']:
                        marker['info'] = markdown_to_html(marker['info'], trim=True)
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
        return '[MAP ' + codecs.encode(json.dumps(the_map).encode('utf8'), 'base64').decode().replace('\n', '') + ']'
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
    args = dict(yaml_filename=this_thread.current_info['yaml_filename'], user=this_thread.current_info['user'], user_code=this_thread.current_info['session'], secret=this_thread.current_info['secret'], url=this_thread.current_info['url'], url_root=this_thread.current_info['url_root'], language=language, psm=psm, x=x, y=y, W=W, H=H, extra=ui_notification, message=message)
    collector = server.ocr_finalize.s(**args)
    todo = list()
    for item in docassemble.base.ocr.ocr_page_tasks(image_file, **args):
        todo.append(server.ocr_page.s(**item))
    the_chord = chord(todo)(collector)
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
    langs = docassemble.base.ocr.get_available_languages()
    if language is None:
        language = get_language()
    ocr_langs = get_config("ocr languages")
    if ocr_langs is None:
        ocr_langs = dict()
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
                    logmessage("ocr_file: could not get OCR language for language " + str(language) + "; using language " + str(lang))
            except Exception as the_error:
                if 'eng' in langs:
                    lang = 'eng'
                else:
                    lang = langs[0]
                logmessage("ocr_file: could not get OCR language for language " + str(language) + "; using language " + str(lang) + "; error was " + str(the_error))
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
                result = subprocess.call(args)
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
            text = subprocess.check_output(['tesseract', 'stdin', 'stdout', '-l', str(lang), '-psm', str(psm)], stdin=file_to_read, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            raise Exception("ocr_file: failed to list available languages: " + str(err) + " " + str(err.output))
        page_text.append(text.decode('utf8'))
    for directory in temp_directory_list:
        shutil.rmtree(directory)
    return "\f".join(page_text)

def path_and_mimetype(file_ref):
    """Returns a path and the MIME type of a file"""
    if isinstance(file_ref, DAFile):
        if hasattr(file_ref, 'mimetype'):
            mime_type = file_ref.mimetype
        else:
            mime_type = None
        return file_ref.path(), mime_type
    file_info = server.file_finder(file_ref)
    return file_info.get('fullpath', None), file_info.get('mimetype', None)

class DummyObject(object):
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

MachineLearningEntry = DummyObject

def set_machine_learning_entry(target):
    global MachineLearningEntry
    MachineLearningEntry = target
