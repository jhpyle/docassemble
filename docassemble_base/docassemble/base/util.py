# -*- coding: utf-8 -*-
import datetime
import pytz
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError
from docassemble.base.functions import comma_and_list, get_language, set_language, get_dialect, word, comma_list, ordinal, ordinal_number, need, nice_number, quantity_noun, possessify, verb_past, verb_present, noun_plural, noun_singular, space_to_underscore, force_ask, period_list, name_suffix, currency_symbol, currency, indefinite_article, nodoublequote, capitalize, title_case, url_of, do_you, did_you, does_a_b, did_a_b, your, her, his, is_word, get_locale, set_locale, process_action, url_action, get_info, set_info, get_config, prevent_going_back, qr_code, action_menu_item, from_b64_json, defined, value, message, response, command, single_paragraph, location_returned, location_known, user_lat_lon, interview_url, interview_url_action, interview_url_as_qr, interview_url_action_as_qr, objects_from_file, this_thread, static_image, action_arguments, action_argument, default_timezone, language_functions, language_function_constructor, get_default_timezone, user_logged_in, user_privileges, user_has_privilege, user_info
from docassemble.base.core import DAObject, DAList, DADict, DAFile, DAFileCollection, DAFileList, DATemplate, selections
from decimal import Decimal
import sys
#sys.stderr.write("importing async mail now from util\n")
from docassemble.base.filter import file_finder, url_finder, markdown_to_html, async_mail
import dateutil
import dateutil.parser
import json
import codecs
import us
import babel.dates
from bs4 import BeautifulSoup

__all__ = ['ordinal', 'ordinal_number', 'comma_list', 'word', 'get_language', 'set_language', 'get_dialect', 'get_locale', 'set_locale', 'comma_and_list', 'need', 'nice_number', 'quantity_noun', 'currency_symbol', 'verb_past', 'verb_present', 'noun_plural', 'noun_singular', 'indefinite_article', 'capitalize', 'space_to_underscore', 'force_ask', 'period_list', 'name_suffix', 'currency', 'static_image', 'title_case', 'url_of', 'process_action', 'url_action', 'get_info', 'set_info', 'get_config', 'prevent_going_back', 'qr_code', 'action_menu_item', 'from_b64_json', 'defined', 'value', 'message', 'response', 'command', 'single_paragraph', 'location_returned', 'location_known', 'user_lat_lon', 'interview_url', 'interview_url_action', 'interview_url_as_qr', 'interview_url_action_as_qr', 'LatitudeLongitude', 'RoleChangeTracker', 'Name', 'IndividualName', 'Address', 'Person', 'Individual', 'ChildList', 'FinancialList', 'PeriodicFinancialList', 'Income', 'Asset', 'Expense', 'Value', 'PeriodicValue', 'OfficeList', 'Organization', 'objects_from_file', 'send_email', 'email_string', 'map_of', 'selections', 'DAObject', 'DAList', 'DADict', 'DAFile', 'DAFileCollection', 'DAFileList', 'DATemplate', 'us', 'last_access_time', 'last_access_delta', 'last_access_days', 'last_access_hours', 'last_access_minutes', 'action_arguments', 'action_argument', 'timezone_list', 'as_datetime', 'current_datetime', 'date_difference', 'date_interval', 'year_of', 'month_of', 'day_of', 'format_date', 'today', 'get_default_timezone', 'user_logged_in', 'user_privileges', 'user_has_privilege', 'user_info']

def default_user_id_function():
    return dict()

user_id_dict = default_user_id_function

def set_user_id_function(func):
    global user_id_dict
    user_id_dict = func
    return

def today_default(format='long', timezone=default_timezone):
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
    """Interprets the_date as a date and returns the date formatted in long form."""
    try:
        if isinstance(the_date, datetime.datetime) or isinstance(the_date, datetime.date):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return babel.dates.format_date(date, format=format, locale=get_language())
    except:
        return word("Bad date")

class DateTimeDelta(object):
    def __str__(self):
        return quantity_noun(output.days, word('day'))
    pass

def current_datetime(timezone=default_timezone):
    """Returns the current time as a datetime.datetime object with a timezone.
    Uses the default timezone unless another timezone is explicitly provided."""
    return pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(timezone))

def as_datetime(the_date, timezone=default_timezone):
    """Converts the_date to a datetime.datetime object with a timezone.  Uses the
    default timezone unless another timezone is explicitly provided."""
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

def date_difference(a, b, timezone=default_timezone):
    """Calculates the difference between date a and date b.  Returns an
    object with attributes weeks, days, hours, minutes, seconds, and delta."""
    if isinstance(a, datetime.date):
        a = datetime.datetime.combine(a, datetime.datetime.min.time())
    if isinstance(a, datetime.date):
        b = datetime.datetime.combine(b, datetime.datetime.min.time())
    if not isinstance(a, datetime.datetime):
        a = dateutil.parser.parse(a)
    if not isinstance(b, datetime.datetime):
        b = dateutil.parser.parse(b)
    if a.tzinfo:
        a = a.astimezone(pytz.timezone(timezone))
    else:
        a = pytz.timezone(timezone).localize(a)
    if b.tzinfo:
        b = b.astimezone(pytz.timezone(timezone))
    else:
        b = pytz.timezone(timezone).localize(b)
    delta = a - b
    output = DateTimeDelta()
    output.delta = delta
    output.weeks = (delta.days / 7.0) + (delta.seconds / 604800.0)
    output.days = delta.days + (delta.seconds / 86400.0)
    output.hours = (delta.days * 24.0) + (delta.seconds / 3600.0)
    output.minutes = (delta.days * 1440.0) + (delta.seconds / 60.0)
    output.seconds = (delta.days * 86400) + delta.seconds
    return output
    
def email_string(persons, include_name=None):
    if persons is None:
        return None
    if type(persons) is not list:
        persons = [persons]
    result = []
    for person in persons:
        if isinstance(person, Person):
            result.append(person.email_address(include_name=include_name))
        else:
            result.append(str(person))
    return result

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
    lookup_dict = user_id_dict()
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
    def init(self, **kwargs):
        self.gathered = False
        self.known = False
        self.description = ""
        return super(LatitudeLongitude, self).init(**kwargs)
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
        logmessage("set to current")
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
    def init(self):
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
    def __repr__(self):
        return(repr(self.full()))

class IndividualName(Name):
    """The name of an Individual."""
    def defined(self):
        """Returns True if the name has been defined.  Otherwise, returns False."""
        return hasattr(self, 'first')
    def full(self, middle='initial', use_suffix=True):
        """Returns the full name.  Has optional keyword arguments middle 
        and use_suffix."""
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
        return(self.first + " " + self.last)
    def lastfirst(self):
        """Returns the last name followed by a comma, followed by the 
        last name, followed by the suffix (if a suffix exists)."""
        output = self.last + ", " + self.first
        if hasattr(self, 'suffix'):
            output += " " + self.suffix
        return output

class Address(DAObject):
    """A geographic address."""
    def init(self, **kwargs):
        self.initializeAttribute('location', LatitudeLongitude)
        self.geolocated = False
        return super(Address, self).init(**kwargs)
    def __str__(self):
        return(self.block())
    def address_for_geolocation(self):
        """Returns a one-line address.  Primarily used internally for geolocation."""
        output = str(self.address) + ", " + str(self.city) + ", " + str(self.state)
        if hasattr(self, 'zip'):
            output += " " + str(self.zip)
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
        the_address = self.address_for_geolocation()
        logmessage("Trying to geolocate " + str(the_address))
        from geopy.geocoders import GoogleV3
        my_geocoder = GoogleV3()
        results = my_geocoder.geocode(the_address)
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
                            if geo_type in component['types'] and not hasattr(self, addr_type):
                                logmessage("Setting " + str(addr_type) + " to " + str(getattr(results[0], geo_type)) + " from " + str(geo_type))
                                setattr(self, addr_type, component['long_name'])
        else:
            logmessage("valid not ok: result count was " + str(len(results)))
            self.geolocate_success = False
        return self.geolocate_success
    def block(self):
        """Returns the address formatted as a block, as in a mailing."""
        output = str(self.address) + " [NEWLINE] "
        if hasattr(self, 'unit') and self.unit:
            output += str(self.unit) + " [NEWLINE] "
        output += str(self.city) + ", " + str(self.state) + " " + str(self.zip)
        return(output)
    def line_one(self):
        """Returns the first line of the address, including the unit 
        number if there is one."""
        output = str(self.address)
        if hasattr(self, 'unit') and self.unit:
            output += ", " + str(self.unit)
        return(output)
    def line_two(self):
        """Returns the second line of the address, including the city,
        state and zip code."""
        output = str(self.city) + ", " + str(self.state) + " " + str(self.zip)
        return(output)

class Person(DAObject):
    """Represents a legal or natural person."""
    def init(self, **kwargs):
        self.initializeAttribute('name', Name)
        self.initializeAttribute('address', Address)
        self.initializeAttribute('location', LatitudeLongitude)
        if 'name' in kwargs:
            self.name.text = kwargs['name']
            del kwargs['name']
        self.roles = set()
        return super(Person, self).init(**kwargs)
    def _map_info(self):
        if not self.location.known:
            if (self.address.location.gathered and self.address.location.known) or self.address.geolocate():
                self.location = self.address.location
        if self.location.gathered and self.location.known:
            if self.name.defined():
                the_info = self.name.full()
            else:
                the_info = capitalize(self.object_name())
            the_info += ' [NEWLINE] ' + self.location.description
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
        if attrname == 'name' and type(value) == str:
            self.name.text = value
        else:
            self.__dict__[attrname] = value
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
            output = is_word(self.full(), **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def is_user(self):
        """Returns True if the person is the user, otherwise False."""
        return self is this_thread.user
    def address_block(self):
        """Return's the person name address as a block, for use in mailings."""
        return("[FLUSHLEFT] " + self.name.full() + " [NEWLINE] " + self.address.block())
    def email_address(self, include_name=None):
        """Returns an e-mail address for the person"""
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
        """Given a verb like "eat," returns "do you eat" or "does John Smith eat,"
        depending on whether the person is the user."""
        if self == this_thread.user:
            return(did_you(the_verb, **kwargs))
        else:
            return(did_a_b(self.name, the_verb, **kwargs))
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
            tense = '1sg'
        else:
            tense = '3sg'
        return verb_past(the_verb, tense)

class Individual(Person):
    """Represents a natural person."""
    def init(self, **kwargs):
        self.initializeAttribute('name', IndividualName)
        self.initializeAttribute('child', ChildList)
        self.initializeAttribute('income', Income)
        self.initializeAttribute('asset', Asset)
        self.initializeAttribute('expense', Expense)
        return super(Individual, self).init(**kwargs)
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
    def init(self, **kwargs):
        self.object_type = Individual
        return super(ChildList, self).init(**kwargs)

class FinancialList(DADict):
    """Represents a set of currency amounts."""
    def init(self, **kwargs):
        self.object_type = Value
        return super(FinancialList, self).init(**kwargs)
    def total(self):
        """Returns the total value in the list, gathering the list items if necessary."""
        if self.gathered:
            result = 0
            for item in self.elements:
                if self[item].exists:
                    result += Decimal(self[item].value)
            return(result)
    def total_gathered(self):
        """Returns the total value in the list, for items gathered so far."""
        result = 0
        for item in self.elements:
            elem = self.elements[item]
            if hasattr(elem, 'exists') and hasattr(elem, 'value'):
                if elem.exists:
                    result += Decimal(elem.value)
        return(result)
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
    def init(self, **kwargs):
        self.object_type = PeriodicValue
        return super(FinancialList, self).init(**kwargs)
    def total(self, period_to_use=1):
        """Returns the total periodic value in the list, gathering the list items if necessary."""
        if self.gathered:
            result = 0
            if period_to_use == 0:
                return(result)
            for item in self.elements:
                if self.elements[item].exists:
                    result += Decimal(self.elements[item].value) * Decimal(self.elements[item].period)
            return(result/Decimal(period_to_use))
    def total_gathered(self, period_to_use=1):
        """Returns the total periodic value in the list, for items gathered so far."""
        result = 0
        if period_to_use == 0:
            return(result)
        for item in self.elements:
            elem = getattr(self, item)
            if hasattr(elem, 'exists') and hasattr(elem, 'value') and hasattr(elem, 'period'):
                if elem.exists:
                    result += Decimal(elem.value * Decimal(elem.period))
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
    """A FinancialList representing a person's assets"""
    pass

class Expense(PeriodicFinancialList):
    """A PeriodicFinancialList representing a person's expenses"""
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
        logmessage("period is a " + str(type(self.period).__name__))
        return (Decimal(self.value) * Decimal(self.period)) / Decimal(period_to_use)

class OfficeList(DAList):
    """Represents a list of offices of a company or organization."""
    def init(self, **kwargs):
        self.object_type = Address
        return super(OfficeList, self).init(**kwargs)

class Organization(Person):
    """Represents a company or organization."""
    def init(self, **kwargs):
        self.initializeAttribute('office', OfficeList)
        if 'offices' in kwargs:
            if type(kwargs['offices']) is list:
                for office in kwargs['offices']:
                    if type(office) is dict:
                        new_office = self.office.appendObject(Address, **office)
                        new_office.geolocate()
            del kwargs['offices']
        return super(Organization, self).init(**kwargs)
    def will_handle(self, problem=None, county=None):
        """Returns True or False depending on whether the organization 
        serves the given county and/or handles the given problem."""
        logmessage("Testing " + str(problem) + " against " + str(self.handles))
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
                the_info += ' [NEWLINE] ' + office.location.description
                this_response = {'latitude': office.location.latitude, 'longitude': office.location.longitude, 'info': the_info}
                if hasattr(office, 'icon'):
                    this_response['icon'] = office.icon
                elif hasattr(self, 'icon'):
                    this_response['icon'] = self.icon
                the_response.append(this_response)
        if len(the_response):
            return the_response
        return None

def send_email(to=None, sender=None, cc=None, bcc=None, template=None, body=None, html=None, subject="", attachments=[]):
    """Sends an e-mail and returns whether sending the e-mail was successful."""
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
    email_stringer = lambda x: email_string(x, include_name=False)
    msg = Message(subject, sender=email_stringer(sender), recipients=email_stringer(to), cc=email_stringer(cc), bcc=email_stringer(bcc), body=body, html=html)
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
        else:
            success = False
        if success:
            for the_attachment in attachment_list:
                if the_attachment.ok:
                    file_info = file_finder(str(the_attachment.number))
                    if ('path' in file_info):
                        failed = True
                        with open(file_info['path'], 'rb') as fp:
                            msg.attach(the_attachment.filename, file_info['mimetype'], fp.read())
                            failed = False
                        if failed:
                            success = False
                    else:
                        success = False
    # appmail = mail_variable()
    # if not appmail:
    #     success = False
    if success:
        try:
            # appmail.send(msg)
            logmessage("Starting to send")
            async_mail(msg)
            logmessage("Finished sending")
        except Exception as errmess:
            logmessage("Sending mail failed: " + str(errmess))
            success = False
    return(success)

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
                        marker['icon'] = {'url': url_finder(marker['icon'])}
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
        return '[MAP ' + codecs.encode(json.dumps(the_map).encode('utf-8'), 'base64').decode().replace('\n', '') + ']'
    return '(Unable to display map)'
    
