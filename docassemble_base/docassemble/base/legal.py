from docassemble.base.core import DAObject, DAList, DAFile, DAFileCollection, DAFileList, DATemplate, selections
from docassemble.base.util import comma_and_list, get_language, set_language, get_dialect, word, comma_list, ordinal, ordinal_number, need, nice_number, possessify, verb_past, verb_present, noun_plural, space_to_underscore, force_ask, period_list, name_suffix, currency, indefinite_article, today, nodoublequote, capitalize, title_case, url_of, do_you, does_a_b, your, her, his, the, in_the, a_in_the_b, of_the, get_locale, set_locale, process_action, url_action, get_info, set_info, get_config, prevent_going_back, qr_code, action_menu_item, from_b64_json
from docassemble.base.filter import file_finder, url_finder, mail_variable, markdown_to_html, async_mail
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError
from datetime import date
import datetime
import dateutil.relativedelta
import dateutil.parser
import json
import inspect
import codecs
import re
import urllib
import sys
import threading
import html2text
import yaml
import us
from decimal import Decimal

__all__ = ['update_info', 'interview_url', 'Court', 'Case', 'Jurisdiction', 'Document', 'LegalFiling', 'Person', 'Individual', 'DAList', 'PartyList', 'ChildList', 'FinancialList', 'PeriodicFinancialList', 'Income', 'Asset', 'LatitudeLongitude', 'RoleChangeTracker', 'DATemplate', 'Expense', 'Value', 'PeriodicValue', 'DAFile', 'DAFileCollection', 'DAFileList', 'send_email', 'comma_and_list', 'get_language', 'get_dialect', 'set_language', 'word', 'comma_list', 'ordinal', 'ordinal_number', 'need', 'nice_number', 'verb_past', 'verb_present', 'noun_plural', 'space_to_underscore', 'force_ask', 'period_list', 'name_suffix', 'currency', 'indefinite_article', 'today', 'capitalize', 'title_case', 'url_of', 'get_locale', 'set_locale', 'process_action', 'url_action', 'selections', 'get_info', 'set_info', 'user_lat_lon', 'location_known', 'location_returned', 'get_config', 'map_of', 'objects_from_file', 'us', 'prevent_going_back', 'month_of', 'day_of', 'year_of', 'qr_code', 'interview_url_as_qr', 'action_menu_item', 'from_b64_json']

class ThreadVariables(threading.local):
    user = None
    role = None
    current_info = dict()
    initialized = False
    def __init__(self, **kw):
        if self.initialized:
            raise SystemError('__init__ called too many times')
        self.initialized = True
        self.__dict__.update(kw)

this_thread = ThreadVariables()

def update_info(new_user, new_role, new_current_info, **kwargs):
    """Transmits information to docassemble about who the current user is,
    what the current user's role is, and other information, such as whether
    the user is logged in and the user's latitude and longitude as 
    determined from GPS.  Always called within an initial block."""
    #logmessage("Updating info!")
    this_thread.user = new_user
    this_thread.role = new_role
    this_thread.current_info = new_current_info
    for att, value in kwargs.iteritems():
        setattr(this_thread, att, value)
    return

def location_returned():
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
    if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and type(this_thread.current_info['user']['location']) is dict and 'latitude' in this_thread.current_info['user']['location']:
        return True
    return False

class LatitudeLongitude(DAObject):
    """Represents a GPS location."""
    def init(self, **kwargs):
        self.gathered = False
        self.known = False
        self.description = ""
        return super(LatitudeLongitude, self).init(**kwargs)
    def status(self):
        #logmessage("got to status")
        if self.gathered:
            #logmessage("gathered is true")
            return False
        else:
            if location_returned():
                #logmessage("returned is true")
                self.set_to_current()
                return False
            else:
                return True
    def set_to_current(self):
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

def user_lat_lon():
    if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and type(this_thread.current_info['user']['location']) is dict:
        if 'latitude' in this_thread.current_info['user']['location'] and 'longitude' in this_thread.current_info['user']['location']:
            return this_thread.current_info['user']['location']['latitude'], this_thread.current_info['user']['location']['longitude']
        elif 'error' in this_thread.current_info['user']['location']:
            return this_thread.current_info['user']['location']['error'], this_thread.current_info['user']['location']['error']
    return None, None

def interview_url(**kwargs):
    """Returns a URL that is direct link to the interview and the current
    variable store.  This is used in multi-user interviews to invite
    additional users to participate. This function depends on
    update_info() having been run in "initial" code."""
    args = kwargs
    args['i'] = this_thread.current_info['yaml_filename']
    args['session'] = this_thread.current_info['session']
    return str(this_thread.current_info['url']) + '?' + '&'.join(map((lambda (k, v): str(k) + '=' + urllib.quote(str(v))), args.iteritems()))

def interview_url_as_qr(**kwargs):
    return qr_code(interview_url(**kwargs))

class Court(DAObject):
    """Represents a court of law."""
    def __str__(self):
        return(self.name)
    def __repr__(self):
        return(repr(self.name))

class Case(DAObject):
    """Represents a case in court."""
    def init(self, **kwargs):
        self.initializeAttribute('defendant', PartyList)
        self.initializeAttribute('plaintiff', PartyList)
        self.firstParty = self.plaintiff
        self.secondParty = self.defendant
        self.case_id = ""
        return super(Case, self).init(**kwargs)
    def role_of(self, party):
        for partyname in dir(self):
            if not isinstance(getattr(self, partyname), PartyList):
                continue
            if getattr(self, partyname).gathered:
                for indiv in getattr(self, partyname):
                    if indiv is party:
                        return partyname
        return 'third party'
    def all_known_people(self):
        output_list = list()
        for partyname in dir(self):
            if not isinstance(getattr(self, partyname), PartyList):
                continue
            for party in getattr(self, partyname).elements:
                if party not in output_list and party.identified():
                    output_list.append(party)
                    if hasattr(party, 'child'):
                        for child in party.child.elements:
                            if child not in output_list and child.identified():
                                output_list.append(child)
        return(output_list)
    def parties(self):
        output_list = list()
        for partyname in dir(self):
            if not isinstance(getattr(self, partyname), PartyList):
                continue
            if getattr(self, partyname).gathered:
                for indiv in getattr(self, partyname):
                    if indiv not in output_list:
                        output_list.append(indiv)
        return(output_list)

class Jurisdiction(DAObject):
    """Represents a jurisdiction, e.g. of a Court.  No functionality 
    implemented yet."""
    pass

class Document(DAObject):
    """This is a base class for different types of documents."""
    def init(self, **kwargs):
        self.title = None
        return super(Document, self).init(**kwargs)

class LegalFiling(Document):
    """Represents a document filed in court."""
    def caption(self):
        self.case.firstParty.gathered
        self.case.secondParty.gathered
        output = ""
        output += "[BOLDCENTER] " + (word("In the") + " " + self.case.court.name).upper() + "\n\n"
        output += "[BEGIN_CAPTION]"
        output += comma_and_list(self.case.firstParty.elements, comma_string=",[NEWLINE]", and_string=word('and'), before_and=" ", after_and='[NEWLINE]') + ",[NEWLINE]"
        output += "[TAB][TAB]" + word(self.case.firstParty.as_noun()).capitalize() + "[NEWLINE] "
        output += "[SKIPLINE][TAB]" + word('v.') + " [NEWLINE][SKIPLINE] "
        output += comma_and_list(self.case.secondParty.elements, comma_string=",[NEWLINE]", and_string=word('and'), before_and=" ", after_and='[NEWLINE]') + ",[NEWLINE]"
        output += "[TAB][TAB]" + word(self.case.secondParty.as_noun()).capitalize()
        output += "[VERTICAL_LINE]"
        output += word('Case No.') + " " + self.case.case_id
        output += "[END_CAPTION]\n\n"
        if self.title is not None:
            output += "[BOLDCENTER] " + self.title.upper() + "\n"
        return(output)

class RoleChangeTracker(DAObject):
    """Used within an interview to facilitate changes in the active role
    required for filling in interview information.  Ensures that participants
    do not receive multiple e-mails needlessly."""
    def init(self):
        self.last_role = None
        return
    def should_send_email(self):
        return True
    def update(self, target_role):
        self.last_role = target_role
        return
    def send_email(self, roles_needed, **kwargs):
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
                        self.update(role_needed)
                    return result
        return False

class Name(DAObject):
    def full(self):
        return(self.text)
    def defined(self):
        return hasattr(self, 'text')
    def __str__(self):
        return(self.full())
    def __repr__(self):
        return(repr(self.full()))

class IndividualName(Name):
    def defined(self):
        return hasattr(self, 'first')
    def full(self, middle='initial', use_suffix=True):
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
        return(self.first + " " + self.last)
    def lastfirst(self):
        output = self.last + ", " + self.first
        if hasattr(self, 'suffix'):
            output += " " + self.suffix
        return output

class Address(DAObject):
    def init(self, **kwargs):
        self.initializeAttribute('location', LatitudeLongitude)
        self.geolocated = False
        return super(Address, self).init(**kwargs)
    def __str__(self):
        return(self.block())
    def address_for_geolocation(self):
        output = str(self.address) + ", " + str(self.city) + ", " + str(self.state)
        if hasattr(self, 'zip'):
            output += " " + str(self.zip)
        return output
    def geolocate(self):
        if self.geolocated:
            return self.geolocate_success    
        the_address = self.address_for_geolocation()
        logmessage("Trying to geolocate " + str(the_address))
        from pygeocoder import Geocoder
        google_config = get_config('google')
        if google_config and 'api key' in google_config:
            my_geocoder = Geocoder(api_key=google_config['api key'])
        else:
            my_geocoder = Geocoder()
        results = my_geocoder.geocode(the_address)
        self.geolocated = True
        if len(results):
            self.geolocate_success = True
            self.location.gathered = True
            self.location.known = True
            self.location.latitude = results[0].coordinates[0]
            self.location.longitude = results[0].coordinates[1]
            self.location.description = self.block()
            self.geolocate_response = results.raw
            geo_types = {'administrative_area_level_2': 'county', 'neighborhood': 'neighborhood', 'postal_code': 'zip', 'country': 'country'}
            for geo_type, addr_type in geo_types.iteritems():
                if hasattr(results[0], geo_type) and not hasattr(self, addr_type):
                    logmessage("Setting " + str(addr_type) + " to " + str(getattr(results[0], geo_type)) + " from " + str(geo_type))
                    setattr(self, addr_type, getattr(results[0], geo_type))
                #else:
                    #logmessage("Not setting " + addr_type + " from " + geo_type)
            #logmessage(json.dumps(self.geolocate_response))
        else:
            logmessage("valid not ok: result count was " + str(len(results)))
            self.geolocate_success = False
        return self.geolocate_success
    def block(self):
        output = str(self.address) + " [NEWLINE] "
        if hasattr(self, 'unit') and self.unit:
            output += str(self.unit) + " [NEWLINE] "
        output += str(self.city) + ", " + str(self.state) + " " + str(self.zip)
        return(output)
    def line_one(self):
        output = str(self.address)
        if hasattr(self, 'unit') and self.unit:
            output += ", " + str(self.unit)
        return(output)
    def line_two(self):
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
    def map_info(self):
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
    def object_possessive(self, target):
        if self is this_thread.user:
            return your(target)
        return super(Person, self).object_possessive(target)
    def is_are_you(self, **kwargs):
        if self is this_thread.user:
            output = 'are you'
        else:
            output = 'is ' + str(self.name)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def is_user(self):
        return self is this_thread.user
    def address_block(self):
        return("[FLUSHLEFT] " + self.name.full() + " [NEWLINE] " + self.address.block())
    def email_address(self, include_name=None):
        if include_name is True or (hasattr(self.name, 'first') and include_name is not False):
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
        if self == this_thread.user:
            return(do_you(the_verb, **kwargs))
        else:
            return(does_a_b(self.name, the_verb, **kwargs))
    def does_verb(self, the_verb, **kwargs):
        if self == this_thread.user:
            tense = 1
        else:
            tense = 3
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            return verb_past(the_verb, person=tense)
        else:
            return verb_present(the_verb, person=tense)
    def did_verb(self, the_verb, **kwargs):
        if self == this_thread.user:
            tense = 1
        else:
            tense = 3
        return verb_past(the_verb, person=tense)

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
        if hasattr(self.name, 'first'):
            return True
        return False
    def age_in_years(self, decimals=False):
        """Returns the individual's age in years, based on self.birthdate."""
        if hasattr(self, 'age'):
            if decimals:
                return float(self.age)
            else:
                return int(self.age)
        rd = dateutil.relativedelta.relativedelta(datetime.datetime.now(), dateutil.parser.parse(self.birthdate))
        if decimals:
            return float(rd.years)
        else:
            return int(rd.years)
    def first_name_hint(self):
        if self is this_thread.user and this_thread.current_info['user']['is_authenticated'] and 'firstname' in this_thread.current_info['user'] and this_thread.current_info['user']['firstname']:
            return this_thread.current_info['user']['firstname'];
        return ''
    def last_name_hint(self):
        if self is this_thread.user and this_thread.current_info['user']['is_authenticated'] and 'lastname' in this_thread.current_info['user'] and this_thread.current_info['user']['lastname']:
            return this_thread.current_info['user']['lastname'];
        return ''
    def possessive(self, target):
        if self is this_thread.user:
            return your(target)
        else:
            return possessify(self.name, target)
    def do_verb(self, verb):
        if self is this_thread.user:
            return ""
        else:
            return possessify(self.name, target)
    def salutation(self):
        if self.gender == 'female':
            return('Ms.')
        else:
            return('Mr.')
    def pronoun_possessive(self, target, **kwargs):
        if self == this_thread.user and ('thirdperson' not in kwargs or not kwargs['thirdperson']):
            output = your(target)
        elif self.gender == 'female':
            output = her(target)
        else:
            output = his(target)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        if self == this_thread.user:
            output = word('you')
        if self.gender == 'female':
            output = word('her')
        else:
            output = word('him')
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def pronoun_objective(self, **kwargs):
        return self.pronoun(**kwargs)
    def pronoun_subjective(self, **kwargs):
        if self == this_thread.user and ('thirdperson' not in kwargs or not kwargs['thirdperson']):
            output = word('you')
        elif self.gender == 'female':
            output = word('she')
        else:
            output = word('he')
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def yourself_or_name(self, **kwargs):
        if self == this_thread.user:
            output = word('yourself')
        else:
            output = self.name.full()
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)

class PartyList(DAList):
    """Represents a list of parties to a case.  The default object
    type for items in the list is Individual."""
    def init(self, **kwargs):
        self.object_type = Individual
        return super(PartyList, self).init(**kwargs)

class ChildList(DAList):
    def init(self, **kwargs):
        self.object_type = Individual
        return super(ChildList, self).init(**kwargs)

class FinancialList(DAObject):
    def init(self, **kwargs):
        self.elements = set()
        self.gathering = False
        return super(FinancialList, self).init(**kwargs)
    def new(self, item, **kwargs):
        self.initializeAttribute(item, Value)
        self.elements.add(item)
        for arg in kwargs:
            setattr(getattr(self, item), arg, kwargs[arg])
    def total(self):
        if self.gathered:
            result = 0
            for item in self.elements:
                if getattr(self, item).exists:
                    result += Decimal(getattr(self, item).value)
            return(result)
    def total_gathered(self):
        result = 0
        for item in self.elements:
            elem = getattr(self, item)
            if hasattr(elem, 'exists') and hasattr(elem, 'value'):
                if elem.exists:
                    result += Decimal(elem.value)
        return(result)
    def __str__(self):
        return self.total()
    
class PeriodicFinancialList(DAObject):
    def init(self, **kwargs):
        self.elements = set()
        self.gathering = False
        return super(PeriodicFinancialList, self).init(**kwargs)
    def new(self, item, **kwargs):
        self.initializeAttribute(item, PeriodicValue)
        self.elements.add(item)
        for arg in kwargs:
            setattr(getattr(self, item), arg, kwargs[arg])
    def total(self):
        if self.gathered:
            result = 0
            for item in self.elements:
                if getattr(self, item).exists:
                    result += Decimal(getattr(self, item).value) * Decimal(getattr(self, item).period)
            return(result)
    def total_gathered(self):
        result = 0
        for item in self.elements:
            elem = getattr(self, item)
            if hasattr(elem, 'exists') and hasattr(elem, 'value') and hasattr(elem, 'period'):
                if elem.exists:
                    result += Decimal(elem.value * Decimal(elem.period))
        return(result)
    def __str__(self):
        return self.total()

class Income(PeriodicFinancialList):
    pass

class Asset(FinancialList):
    pass

class Expense(PeriodicFinancialList):
    pass

class Value(DAObject):
    pass

class PeriodicValue(Value):
    pass

class OfficeList(DAList):
    def init(self, **kwargs):
        self.object_type = Address
        return super(OfficeList, self).init(**kwargs)

class Organization(Person):
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
        logmessage("Testing " + str(problem) + " against " + str(self.handles))
        if problem:
            if not (hasattr(self, 'handles') and problem in self.handles):
                return False
        if county:
            if not (hasattr(self, 'serves') and county in self.serves):
                return False
        return True
    def map_info(self):
        response = list()
        for office in self.office:
            if (office.location.gathered and office.location.known) or office.geolocate():
                if self.name.defined():
                    the_info = self.name.full()
                else:
                    the_info = capitalize(self.object_name())
                the_info += ' [NEWLINE] ' + office.location.description
                this_response = {'latitude': office.location.latitude, 'longitude': office.location.longitude, 'info': the_info}
                if hasattr(self, 'icon'):
                    this_response['icon'] = self.icon
                response.append(this_response)
        if len(response):
            return response
        return None

def objects_from_file(file_ref):
    file_info = file_finder(file_ref)
    if 'path' not in file_info:
        raise SystemError('objects_from_file: file reference ' + str(file_ref) + ' not found')
    objects = list()
    with open(file_info['fullpath'], 'r') as fp:
        for document in yaml.load_all(fp):
            if type(document) is not dict:
                raise SystemError('objects_from_file: file reference ' + str(file_ref) + ' contained a document that was not a YAML dictionary')
            if len(document):
                if not ('object' in document and 'items' in document):
                    raise SystemError('objects_from_file: file reference ' + str(file_ref) + ' contained a document that did not contain an object and items declaration')
                if type(document['items']) is not list:
                    raise SystemError('objects_from_file: file reference ' + str(file_ref) + ' contained a document the items declaration for which was not a dictionary')
                constructor = None
                if document['object'] in globals():
                    contructor = globals()[document['object']]
                elif document['object'] in locals():
                    contructor = locals()[document['object']]
                if not constructor:
                    if 'module' in document:
                        new_module = __import__(document['module'], globals(), locals(), [document['object']], -1)
                        constructor = getattr(new_module, document['object'], None)
                if not constructor:
                    raise SystemError('objects_from_file: file reference ' + str(file_ref) + ' contained a document for which the object declaration, ' + str(document['object']) + ' could not be found')
                for item in document['items']:
                    if type(item) is not dict:
                        raise SystemError('objects_from_file: file reference ' + str(file_ref) + ' contained an item, ' + str(item) + ' that was not expressed as a dictionary')
                    objects.append(constructor(**item))
    return objects

def send_email(to=None, sender=None, cc=None, bcc=None, template=None, body=None, html=None, subject="", attachments=[]):
    """Sends an e-mail"""
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
            body = html2text.html2text(body_html)
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
                        with open(file_info['path'], 'r') as fp:
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

def month_of(the_date, as_word=False):
    """Interprets the_date as a date and returns the month.  
    Set as_word to True if you want the month as a word."""
    date = dateutil.parser.parse(the_date)
    try:
        if as_word:
            return(date.strftime('%B'))
        return(date.strftime('%m'))
    except:
        return word("Bad date")

def day_of(the_date):
    """Interprets the_date as a date and returns the day of month."""
    date = dateutil.parser.parse(the_date)
    try:
        return(date.strftime('%d'))
    except:
        return word("Bad date")

def year_of(the_date):
    """Interprets the_date as a date and returns the year."""
    date = dateutil.parser.parse(the_date)
    try:
        return(date.strftime('%Y'))
    except:
        return word("Bad date")

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

def map_of(*pargs, **kwargs):
    """Shows a Google Map"""
    the_map = {'markers': list()}
    all_args = list()
    for arg in pargs:
        if type(arg) is list:
            all_args.extend(arg)
        else:
            all_args.append(arg)
    for arg in all_args:
        if isinstance(arg, DAObject):
            markers = arg.map_info()
            if markers:
                for marker in markers:
                    if 'icon' in marker and type(marker['icon']) is not dict:
                        marker['icon'] = {'url': url_finder(marker['icon'])}
                    if 'info' in marker and marker['info']:
                        marker['info'] = markdown_to_html(marker['info'], trim=True)
                    the_map['markers'].append(marker)
    if 'center' in kwargs:
        the_center = kwargs['center']
        if callable(getattr(the_center, 'map_info', None)):
            markers = the_center.map_info()
            if markers:
                the_map['center'] = markers[0]
    if 'center' not in the_map and len(the_map['markers']):
        the_map['center'] = the_map['markers'][0]
    if len(the_map['markers']) or 'center' in the_map:
        return '[MAP ' + codecs.encode(json.dumps(the_map).encode('utf-8'), 'base64').decode().replace('\n', '') + ']'
    return '(Unable to display map)'
