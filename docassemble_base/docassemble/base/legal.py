from docassemble.base.core import DAObject, DAList, DAFile, DAFileCollection, DAFileList
from docassemble.base.util import comma_and_list, get_language, set_language, word, comma_list, ordinal, ordinal_number, need, nice_number, possessify, verb_past, verb_present, noun_plural, space_to_underscore, force_ask, period_list, currency, indefinite_article, today, nodoublequote, capitalize, title_case, url_of, do_you, does_a_b, your, her, his, the, in_the, a_in_the_b, of_the, get_locale, set_locale, process_action, url_action
from docassemble.base.filter import file_finder, url_finder, mail_variable, markdown_to_html
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError
from datetime import date
import inspect
import re
import urllib
import sys
import threading
from decimal import Decimal

__all__ = ['update_info', 'interview_url', 'Court', 'Case', 'Jurisdiction', 'Document', 'LegalFiling', 'Person', 'Individual', 'DAList', 'PartyList', 'ChildList', 'FinancialList', 'PeriodicFinancialList', 'Income', 'Asset', 'RoleChangeTracker', 'DATemplate', 'Expense', 'Value', 'PeriodicValue', 'DAFile', 'DAFileCollection', 'DAFileList', 'send_email', 'comma_and_list', 'get_language', 'set_language', 'word', 'comma_list', 'ordinal', 'ordinal_number', 'need', 'nice_number', 'verb_past', 'verb_present', 'noun_plural', 'space_to_underscore', 'force_ask', 'period_list', 'currency', 'indefinite_article', 'today', 'nodoublequote', 'capitalize', 'title_case', 'url_of', 'get_locale', 'set_locale', 'process_action', 'url_action']

this_thread = threading.local()
this_thread.user = None
this_thread.role = None
this_thread.current_info = dict()

def update_info(new_user, new_role, new_current_info):
    this_thread.user = new_user
    this_thread.role = new_role
    this_thread.current_info = new_current_info
    return

def interview_url():
    return str(this_thread.current_info['url']) + '?i=' + urllib.quote(this_thread.current_info['yaml_filename']) + '&session=' + urllib.quote(this_thread.current_info['session'])

class Court(DAObject):
    def __str__(self):
        return(self.name)
    def __repr__(self):
        return(self.name)

class Case(DAObject):
    def init(self):
        self.initializeAttribute(name='plaintiff', objectType=PartyList)
        self.initializeAttribute(name='defendant', objectType=PartyList)
        self.firstParty = self.plaintiff
        self.secondParty = self.defendant
        self.case_id = ""
        return super(Case, self).init()
    def role_of(self, party):
        for partyname in ['plaintiff', 'defendant', 'petitioner', 'respondent']:
            if hasattr(self, partyname) and getattr(self, partyname).gathered:
                for indiv in getattr(self, partyname):
                    if indiv is party:
                        return partyname
        return 'third party'
    def parties(self):
        output_list = list()
        for partyname in ['plaintiff', 'defendant', 'petitioner', 'respondent']:
            if hasattr(self, partyname) and getattr(self, partyname).gathered:
                for indiv in getattr(self, partyname):
                    if indiv not in output_list:
                        output_list.append(indiv)
        return(output_list)

class Jurisdiction(DAObject):
    pass

class Document(DAObject):
    pass

class LegalFiling(Document):
    def init(self):
        self.title = None
        return super(Document, self).init()
    def caption(self):
        self.case.firstParty.gathered
        self.case.secondParty.gathered
        output = ""
        output += "[BOLDCENTER] " + (word("In the") + " " + self.case.court.name).upper() + "\n\n"
        output += "[BEGIN_CAPTION]"
        output += comma_and_list(self.case.firstParty.elements, comma_string=",[NEWLINE]", and_string=word('and'), before_and=" ", after_and='[NEWLINE]') + ",[NEWLINE]"
        output += "[TAB][TAB]" + self.case.firstParty.as_noun().capitalize() + "[NEWLINE] "
        output += "[SKIPLINE][TAB]" + word('v.') + " [NEWLINE][SKIPLINE] "
        output += comma_and_list(self.case.secondParty.elements, comma_string=",[NEWLINE]", and_string=word('and'), before_and=" ", after_and='[NEWLINE]') + ",[NEWLINE]"
        output += "[TAB][TAB]" + self.case.secondParty.as_noun().capitalize()
        output += "[VERTICAL_LINE]"
        output += word('Case No.') + " " + self.case.case_id
        output += "[END_CAPTION]\n\n"
        if self.title is not None:
            output += "[BOLDCENTER] " + self.title.upper() + "\n"
        return(output)

class RoleChangeTracker(DAObject):
    def init(self):
        self.last_role = None
        return
    def should_send_email(self):
        return True
    def update(self, target_role):
        self.last_role = target_role
        return
    def send_email(self, roles_needed, **kwargs):
        logmessage("Current role is " + str(this_thread.role))
        for role_option in kwargs:
            if 'to' in kwargs[role_option]:
                need(kwargs[role_option]['to'].email)
        for role_needed in roles_needed:
            logmessage("One role needed is " + str(role_needed))
            if role_needed == self.last_role:
                logmessage("Already notified new role " + str(role_needed))
                return False
            if role_needed in kwargs:
                logmessage("I have info on " + str(role_needed))
                email_info = kwargs[role_needed]
                if 'to' in email_info and 'email' in email_info:
                    logmessage("I have email info on " + str(role_needed))
                    try:
                        result = send_email(to=email_info['to'], html=email_info['email'].content, subject=email_info['email'].subject)
                    except DAError:
                        result = False
                    if result:
                        self.update(role_needed)
                    return result
        return False

class DATemplate(DAObject):
    def init(self, **kwargs):
        if 'content' in kwargs:
            self.content = kwargs['content']
        else:
            self.content = ""
        if 'subject' in kwargs:
            self.subject = kwargs['subject']
        else:
            self.subject = ""
    def __str__(self):
        return(self.content)
    def __repr__(self):
        return(self.content)

class Name(DAObject):
    def full(self):
        return(self.text)
    def __str__(self):
        return(self.full())
    def __repr__(self):
        return(self.full())

class IndividualName(Name):
    def full(self):
        return(self.first + " " + self.last)
    def firstlast(self):
        return(self.first + " " + self.last)
    def lastfirst(self):
        return(self.last + ", " + self.first)
    def __str__(self):
        return(self.full())
    def __repr__(self):
        return(self.full())

class Address(DAObject):
    def __str__(self):
        return(self.block())
    def block(self):
        output = self.address + " [NEWLINE] "
        if hasattr(self, 'unit') and self.unit:
            output += self.unit + " [NEWLINE] "
        output += self.city + ", " + self.state + " " + self.zip
        return(output)
    pass

class Person(DAObject):
    def init(self):
        self.initializeAttribute(name='name', objectType=Name)
        self.initializeAttribute(name='address', objectType=Address)
        self.roles = set()
        return super(Person, self).init()
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
    def age(self):
        if (hasattr(self, 'age_in_years')):
            return self.age_in_years
        today = date.today()
        born = self.birthdate
        try: 
            birthday = born.replace(year=today.year)
        except ValueError:
            birthday = born.replace(year=today.year, month=born.month+1, day=1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year
    def is_question(self, **kwargs):
        if self == this_thread.user:
            return(are_you(the_verb, **kwargs))
        else:
            return(does_a_b(self.name, the_verb, **kwargs))
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
    def init(self):
        self.initializeAttribute(name='name', objectType=IndividualName)
        self.initializeAttribute(name='child', objectType=ChildList)
        self.initializeAttribute(name='income', objectType=Income)
        self.initializeAttribute(name='asset', objectType=Asset)
        self.initializeAttribute(name='expense', objectType=Expense)
        return super(Individual, self).init()
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
    pass

class ChildList(DAList):
    pass

class FinancialList(DAObject):
    def init(self):
        self.elements = set()
        return super(FinancialList, self).init()
    def new(self, item, **kwargs):
        self.initializeAttribute(name=item, objectType=Value)
        self.elements.add(item)
        for arg in kwargs:
            setattr(getattr(self, item), arg, kwargs[arg])
    def total(self):
        result = 0
        for item in self.elements:
            if getattr(self, item).exists:
                result += Decimal(getattr(self, item).value)
        return(result)
    def __str__(self):
        return self.total()
    
class PeriodicFinancialList(DAObject):
    def init(self):
        self.elements = set()
        return super(PeriodicFinancialList, self).init()
    def new(self, item, **kwargs):
        self.initializeAttribute(name=item, objectType=PeriodicValue)
        self.elements.add(item)
        for arg in kwargs:
            setattr(getattr(self, item), arg, kwargs[arg])
    def total(self):
        if not self.gathering:
            self.gathered
        result = 0
        for item in self.elements:
            if getattr(self, item).exists:
                result += Decimal(getattr(self, item).value) * int(getattr(self, item).period)
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

def send_email(to=None, sender=None, cc=None, bcc=None, body=None, html=None, subject="", attachments=[]):
    from flask_mail import Message
    if type(to) is not list:
        to = [to]
    if len(to) == 0:
        return False
    if body is None and html is None:
        body = ""
    email_stringer = lambda x: email_string(x, include_name=False)
    msg = Message(subject, sender=email_stringer(sender), recipients=email_stringer(to), cc=email_stringer(cc), bcc=email_stringer(bcc), body=body, html=html)
    success = True
    for attachment in attachments:
        if type(attachment) is DAFileCollection:
            subattachment = getattr(attachment, 'pdf', getattr(attachment, 'rtf', getattr(attachment, 'tex', None)))
            if subattachment is not None:
                attachment = subattachment
            else:
                success = False
        if type(attachment) is DAFile and attachment.ok:
            file_info = file_finder(str(attachment.number))
            if ('path' in file_info):
                failed = True
                with open(file_info['path'], 'r') as fp:
                    msg.attach(file_info['filename'], file_info['mimetype'], fp.read())
                    failed = False
                if failed:
                    success = False
            else:
                success = False
        else:
            success = False
    appmail = mail_variable()
    if not appmail:
        success = False
    if success:
        try:
            appmail.send(msg)
        except Exception as errmess:
            success = False
    return(success)
    
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
