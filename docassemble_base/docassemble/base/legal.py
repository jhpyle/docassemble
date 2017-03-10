from docassemble.base.core import DAObject, DAList, DADict, DASet, DAFile, DAFileCollection, DAFileList, DAEmail, DAEmailRecipient, DAEmailRecipientList, DATemplate, selections
from docassemble.base.functions import comma_and_list, get_language, set_language, get_dialect, set_country, get_country, word, comma_list, ordinal, ordinal_number, need, nice_number, quantity_noun, possessify, verb_past, verb_present, noun_plural, noun_singular, space_to_underscore, force_ask, force_gather, period_list, name_suffix, currency, indefinite_article, nodoublequote, capitalize, title_case, url_of, do_you, did_you, does_a_b, did_a_b, your, her, his, is_word, get_locale, set_locale, process_action, url_action, get_info, set_info, get_config, prevent_going_back, qr_code, action_menu_item, from_b64_json, defined, value, message, response, json_response, command, single_paragraph, quote_paragraphs, location_returned, location_known, user_lat_lon, interview_url, interview_url_action, interview_url_as_qr, interview_url_action_as_qr, interview_email, get_emails, get_default_timezone, user_logged_in, interface, user_privileges, user_has_privilege, user_info, action_arguments, action_argument, task_performed, task_not_yet_performed, mark_task_as_performed, times_task_performed, set_task_counter, background_action, background_response, background_response_action, us, set_live_help_status, chat_partners_available, phone_number_in_e164, phone_number_is_valid, countries_list, country_name, write_record, read_records, delete_record, variables_as_json, all_variables, language_from_browser, device, plain, bold, italic
from docassemble.base.util import LatitudeLongitude, RoleChangeTracker, Name, IndividualName, Address, Person, Individual, ChildList, FinancialList, PeriodicFinancialList, Income, Asset, Expense, Value, PeriodicValue, OfficeList, Organization, send_email, send_sms, map_of, last_access_time, last_access_delta, last_access_days, last_access_hours, last_access_minutes, timezone_list, as_datetime, current_datetime, date_difference, date_interval, today, month_of, day_of, year_of, format_date, format_time, DARedis, SimpleTextMachineLearner, ocr_file, objects_from_file, get_sms_session, initiate_sms_session, terminate_sms_session, path_and_mimetype

__all__ = ['interview_url', 'Court', 'Case', 'Jurisdiction', 'Document', 'LegalFiling', 'Person', 'Individual', 'DAObject', 'DAList', 'DADict', 'DASet', 'PartyList', 'ChildList', 'FinancialList', 'PeriodicFinancialList', 'Income', 'Asset', 'LatitudeLongitude', 'RoleChangeTracker', 'DATemplate', 'Expense', 'Value', 'PeriodicValue', 'DAFile', 'DAFileCollection', 'DAFileList', 'DAEmail', 'DAEmailRecipient', 'DAEmailRecipientList', 'send_email', 'send_sms', 'comma_and_list', 'get_language', 'get_dialect', 'set_country', 'get_country', 'set_language', 'word', 'comma_list', 'ordinal', 'ordinal_number', 'need', 'nice_number', 'quantity_noun', 'verb_past', 'verb_present', 'noun_plural', 'noun_singular', 'space_to_underscore', 'force_ask', 'force_gather', 'period_list', 'name_suffix', 'currency', 'indefinite_article', 'capitalize', 'title_case', 'url_of', 'get_locale', 'set_locale', 'process_action', 'url_action', 'selections', 'get_info', 'set_info', 'user_lat_lon', 'location_known', 'location_returned', 'get_config', 'map_of', 'objects_from_file', 'prevent_going_back', 'month_of', 'day_of', 'year_of', 'format_date', 'format_time', 'today', 'qr_code', 'interview_url_as_qr', 'interview_url_action_as_qr', 'action_menu_item', 'from_b64_json', 'defined', 'value', 'message', 'response', 'json_response', 'command', 'single_paragraph', 'quote_paragraphs', 'interview_url_action', 'action_arguments', 'action_argument', 'last_access_time', 'last_access_delta', 'last_access_days', 'last_access_hours', 'last_access_minutes', 'timezone_list', 'as_datetime', 'current_datetime', 'date_difference', 'date_interval', 'get_default_timezone', 'user_logged_in', 'interface', 'user_privileges', 'user_has_privilege', 'user_info', 'task_performed', 'task_not_yet_performed', 'mark_task_as_performed', 'times_task_performed', 'set_task_counter', 'background_action', 'background_response', 'background_response_action', 'us', 'DARedis', 'SimpleTextMachineLearner', 'set_live_help_status', 'chat_partners_available', 'phone_number_in_e164', 'phone_number_is_valid', 'countries_list', 'country_name', 'write_record', 'read_records', 'delete_record', 'variables_as_json', 'all_variables', 'ocr_file', 'get_sms_session', 'initiate_sms_session', 'terminate_sms_session', 'language_from_browser', 'device', 'interview_email', 'get_emails', 'plain', 'bold', 'italic', 'path_and_mimetype']

class Court(DAObject):
    """Represents a court of law."""
    def __str__(self):
        return(self.name)
#    def __repr__(self):
#        return(repr("asdf"))

def _add_person_and_children_of(target, output_list):
    if target not in output_list and target.identified():
        output_list.append(target)
        if hasattr(target, 'child'):
            for child in target.child.elements:
                _add_person_and_children_of(child, output_list)

class Case(DAObject):
    """Represents a case in court."""
    def init(self, *pargs, **kwargs):
        self.defendant = PartyList()
        self.plaintiff = PartyList()
        self.firstParty = self.plaintiff
        self.secondParty = self.defendant
        self.case_id = ""
        return super(Case, self).init(*pargs, **kwargs)
    def role_of(self, party):
        """Given a person object, it looks through the parties to the 
        case and returns the name of the party to which the person belongs.
        Returns "third party" if the person is not found among the parties."""
        for partyname in self.__dict__:
            if not isinstance(getattr(self, partyname), PartyList):
                continue
            getattr(self, partyname).trigger_gather()
            for indiv in getattr(self, partyname).elements:
                if indiv is party:
                    return partyname
        return 'third party'
    def all_known_people(self):
        """Returns a list of all parties and their children, 
        children's children, etc.  Does not force the gathering of the
        parties."""
        output_list = list()
        for partyname in self.__dict__:
            if not isinstance(getattr(self, partyname), PartyList):
                continue
            for party in getattr(self, partyname).elements:
                _add_person_and_children_of(party, output_list)
        return(output_list)
    def parties(self):
        """Returns a list of all parties.  Gathers the parties if
        they have not been gathered yet."""
        output_list = list()
        for partyname in self.__dict__:
            if not isinstance(getattr(self, partyname), PartyList):
                continue
            getattr(self, partyname).trigger_gather()
            for indiv in getattr(self, partyname).elements:
                if indiv not in output_list:
                    output_list.append(indiv)
        return(output_list)

class Jurisdiction(DAObject):
    """Represents a jurisdiction, e.g. of a Court.  No functionality 
    implemented yet."""
    pass

class Document(DAObject):
    """This is a base class for different types of documents."""
    def init(self, *pargs, **kwargs):
        self.title = None
        return super(Document, self).init(*pargs, **kwargs)

class LegalFiling(Document):
    """Represents a document filed in court."""
    def caption(self):
        """Returns a case caption for the case, for inclusion in documents."""
        self.case.firstParty.gather()
        self.case.secondParty.gather()
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


class PartyList(DAList):
    """Represents a list of parties to a case.  The default object
    type for items in the list is Individual."""
    def init(self, *pargs, **kwargs):
        self.object_type = Individual
        return super(PartyList, self).init(*pargs, **kwargs)

