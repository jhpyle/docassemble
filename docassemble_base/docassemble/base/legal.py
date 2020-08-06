from docassemble.base.core import DAObject, DAList, DADict, DAOrderedDict, DASet, DAFile, DAFileCollection, DAFileList, DAStaticFile, DAEmail, DAEmailRecipient, DAEmailRecipientList, DATemplate, DAEmpty, DALink, selections, objects_from_file, RelationshipTree, DAContext
from docassemble.base.functions import alpha, roman, item_label, comma_and_list, get_language, set_language, get_dialect, set_country, get_country, word, comma_list, ordinal, ordinal_number, need, nice_number, quantity_noun, possessify, verb_past, verb_present, noun_plural, noun_singular, space_to_underscore, force_ask, force_gather, period_list, name_suffix, currency, indefinite_article, nodoublequote, capitalize, title_case, url_of, do_you, did_you, does_a_b, did_a_b, your, her, his, is_word, get_locale, set_locale, process_action, url_action, get_info, set_info, get_config, prevent_going_back, qr_code, action_menu_item, from_b64_json, defined, value, message, response, json_response, command, single_paragraph, quote_paragraphs, location_returned, location_known, user_lat_lon, interview_url, interview_url_action, interview_url_as_qr, interview_url_action_as_qr, interview_email, get_emails, get_default_timezone, user_logged_in, interface, user_privileges, user_has_privilege, user_info, action_arguments, action_argument, background_action, background_response, background_response_action, background_error_action, us, set_live_help_status, chat_partners_available, phone_number_in_e164, phone_number_formatted, phone_number_is_valid, countries_list, country_name, write_record, read_records, delete_record, variables_as_json, all_variables, language_from_browser, device, plain, bold, italic, states_list, state_name, subdivision_type, indent, raw, fix_punctuation, set_progress, get_progress, referring_url, undefine, invalidate, dispatch, yesno, noyes, split, showif, showifdef, phone_number_part, set_parts, log, encode_name, decode_name, interview_list, interview_menu, server_capabilities, session_tags, get_chat_log, get_user_list, get_user_info, set_user_info, get_user_secret, create_user, create_session, get_session_variables, set_session_variables, get_question_data, go_back_in_session, manage_privileges, redact, forget_result_of, re_run_logic, reconsider, set_title, set_save_status, single_to_double_newlines, verbatim, add_separators, store_variables_snapshot
from docassemble.base.oauth import DAOAuth
from docassemble.base.util import LatitudeLongitude, RoleChangeTracker, Name, IndividualName, Address, City, Event, Person, Thing, Individual, ChildList, FinancialList, PeriodicFinancialList, Income, Asset, Expense, Value, PeriodicValue, OfficeList, Organization, send_email, send_sms, send_fax, map_of, last_access_time, last_access_delta, last_access_days, last_access_hours, last_access_minutes, returning_user, timezone_list, as_datetime, current_datetime, date_difference, date_interval, today, month_of, day_of, dow_of, year_of, format_date, format_datetime, format_time, DARedis, DACloudStorage, DAGoogleAPI, SimpleTextMachineLearner, ocr_file, ocr_file_in_background, read_qr, get_sms_session, initiate_sms_session, terminate_sms_session, path_and_mimetype, run_python_module, pdf_concatenate, include_docx_template, start_time, zip_file, validation_error, DAValidationError, action_button_html, url_ask, overlay_pdf, DAStore, explain, clear_explanations, explanation, set_status, get_status, DAWeb, DAWebError, json, re, iso_country, assemble_docx, docx_concatenate, task_performed, task_not_yet_performed, mark_task_as_performed, times_task_performed, set_task_counter
import copy
from docassemble.base.logger import logmessage

__all__ = [
    'alpha',
    'roman',
    'item_label',
    'interview_url',
    'Court',
    'Case',
    'Document',
    'LegalFiling',
    'Person',
    'Thing',
    'Individual',
    'IndividualName',
    'Name',
    'Address',
    'Organization',
    'City',
    'Event',
    'DAObject',
    'DAList',
    'DADict',
    'DAOrderedDict',
    'DASet',
    'PartyList',
    'ChildList',
    'FinancialList',
    'PeriodicFinancialList',
    'Income',
    'Asset',
    'LatitudeLongitude',
    'RoleChangeTracker',
    'DATemplate',
    'DAEmpty',
    'DALink',
    'Expense',
    'Value',
    'PeriodicValue',
    'DAFile',
    'DAFileCollection',
    'DAFileList',
    'DAStaticFile',
    'DAEmail',
    'DAEmailRecipient',
    'DAEmailRecipientList',
    'send_email',
    'send_sms',
    'send_fax',
    'comma_and_list',
    'get_language',
    'get_dialect',
    'set_country',
    'get_country',
    'set_language',
    'word',
    'comma_list',
    'ordinal',
    'ordinal_number',
    'need',
    'nice_number',
    'quantity_noun',
    'verb_past',
    'verb_present',
    'noun_plural',
    'noun_singular',
    'space_to_underscore',
    'force_ask',
    'force_gather',
    'period_list',
    'name_suffix',
    'currency',
    'indefinite_article',
    'capitalize',
    'title_case',
    'url_of',
    'get_locale',
    'set_locale',
    'process_action',
    'url_action',
    'selections',
    'get_info',
    'set_info',
    'user_lat_lon',
    'location_known',
    'location_returned',
    'get_config',
    'map_of',
    'objects_from_file',
    'prevent_going_back',
    'month_of',
    'day_of',
    'dow_of',
    'year_of',
    'format_date',
    'format_datetime',
    'format_time',
    'today',
    'qr_code',
    'interview_url_as_qr',
    'interview_url_action_as_qr',
    'action_menu_item',
    'from_b64_json',
    'defined',
    'value',
    'message',
    'response',
    'json_response',
    'command',
    'single_paragraph',
    'quote_paragraphs',
    'interview_url_action',
    'action_arguments',
    'action_argument',
    'last_access_time',
    'last_access_delta',
    'last_access_days',
    'last_access_hours',
    'last_access_minutes',
    'returning_user',
    'timezone_list',
    'as_datetime',
    'current_datetime',
    'date_difference',
    'date_interval',
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
    'SimpleTextMachineLearner',
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
    'us_districts',
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
    'store_variables_snapshot'
]

hooks = dict()

class SpecialReturnObject():
    pass

RUN_PARENTS = SpecialReturnObject()

def register_hook(object_type, hook_name, hook, target):
    key = "^".join(target)
    if key not in hooks:
        hooks[key] = dict()
    if object_type not in hooks[key]:
        hooks[key][object_type] = dict()
    #logmessage("Setting hook for " + key + " " + object_type + " " + hook_name)
    hooks[key][object_type][hook_name] = hook

def run_hook(object_type, the_self, hook_name, target, **kwargs):
    while len(target):
        key = "^".join(target)
        #logmessage("Looking for hook for " + key + " and " + hook_name)
        if key in hooks and object_type in hooks[key] and hook_name in hooks[key][object_type]:
            #logmessage("Found a hook for " + key + " " + object_type + " " + hook_name)
            result = hooks[key][object_type][hook_name](the_self, **kwargs)
            #logmessage("Done with hook for " + key + " and " + hook_name)
            if not isinstance(result, SpecialReturnObject):
                return result
        target.pop()
    return None

class Court(DAObject):
    """Represents a court of law."""
    def init(self, *pargs, **kwargs):
        if 'jurisdiction' not in kwargs:
            self.jurisdiction = list()
        return super().init(*pargs, **kwargs)
    def __str__(self):
        return(str(self.name))
    def in_the_court(self, **kwargs):
        """Returns the top line of the first page of a pleading filed in the
        court.

        """
        result = run_hook('court', self, 'in_the_court', self.jurisdiction)
        if result is None:
            return "In the " + self.name
        return result

def _add_person_and_children_of(target, output_list):
    if target not in output_list and target.identified():
        output_list.append(target)
        if hasattr(target, 'child'):
            for child in target.child.elements:
                _add_person_and_children_of(child, output_list)

class Case(DAObject):
    """Represents a case in court."""
    def init(self, *pargs, **kwargs):
        #logmessage("Case init: running")
        self.court = Court()
        self.defendant = PartyList()
        self.plaintiff = PartyList()
        self.firstParty = self.plaintiff
        self.secondParty = self.defendant
        self.is_solo_action = False
        self.state = None
        self.action_type = 'plaintiff defendant'
        return super().init(*pargs, **kwargs)
    def __str__(self):
        return str(self.case_id)
    def set_action_type(self, the_value):
        """Initializes attributes for the different types of parties in the
        case.

        """
        #logmessage("setting action type to " + the_value)
        #logmessage("set_action_type: self instanceName is " + self.instanceName)
        if the_value == 'solo petition':
            if hasattr(self, 'plaintiff'):
                del self.plaintiff
            if hasattr(self, 'defendant'):
                del self.defendant
            if hasattr(self, 'respondent'):
                del self.respondent
            if not hasattr(self, 'petitioner'):
                self.petitioner = PartyList()
            #logmessage("setting firstParty to petitioner")
            self.firstParty = self.petitioner
            #logmessage("firstParty instanceName is " + self.firstParty.instanceName)
            self.is_solo_action = True
        elif the_value == 'in re':
            if hasattr(self, 'plaintiff'):
                del self.plaintiff
            if hasattr(self, 'defendant'):
                del self.defendant
            if hasattr(self, 'respondent'):
                del self.respondent
            if not hasattr(self, 'petitioner'):
                self.petitioner = PartyList()
            self.firstParty = self.petitioner
            self.is_solo_action = True
        elif the_value == 'petition':
            if hasattr(self, 'plaintiff'):
                del self.plaintiff
            if hasattr(self, 'defendant'):
                del self.defendant
            if not hasattr(self, 'petitioner'):
                self.petitioner = PartyList()
            if not hasattr(self, 'respondent'):
                self.respondent = PartyList()
            self.firstParty = self.petitioner
            self.secondParty = self.respondent
            self.is_solo_action = True
        elif the_value == 'plaintiff defendant':
            if not hasattr(self, 'plaintiff'):
                self.plaintiff = PartyList()
            if not hasattr(self, 'defendant'):
                self.defendant = PartyList()
            self.firstParty = self.plaintiff
            self.secondParty = self.defendant
            self.is_solo_action = False
        elif the_value == 'appellee appellant':
            if hasattr(self, 'plaintiff'):
                del self.plaintiff
            if hasattr(self, 'defendant'):
                del self.defendant
            if not hasattr(self, 'appellee'):
                self.appellee = PartyList()
            if not hasattr(self, 'appellant'):
                self.appellant = PartyList()
            self.firstParty = self.appellee
            self.secondParty = self.appellant
            self.is_solo_action = False
        self.action_type = the_value
    def case_id_in_caption(self, **kwargs):
        """Returns the text for the case ID that will appear in the case
        caption.

        """
        result = run_hook('case', self, 'case_id_in_caption', self.court.jurisdiction, **kwargs)
        if result is None:
            if hasattr(self, 'case_id'):
                return word('Case No.') + " " + self.case_id
            else:
                return word('Case No.')
        return result
    def determine_court(self, **kwargs):
        """Runs code, if any exists, to determine what court has jurisdiction
        over the case.

        """
        #logmessage("determine_court 1: firstParty is " + str(self.firstParty.instanceName))
        result = run_hook('case', self, 'determine_court', self.court.jurisdiction, **kwargs)
        #logmessage("determine_court 2: firstParty is " + str(self.firstParty.instanceName))
    def role_of(self, party):
        """Given a person object, it looks through the parties to the
        case and returns the name of the party to which the person belongs.
        Returns "third party" if the person is not found among the parties."""
        for partyname in self.__dict__:
            if not isinstance(getattr(self, partyname), PartyList):
                continue
            if partyname in ['firstParty', 'secondParty']:
                continue
            getattr(self, partyname)._trigger_gather()
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
            getattr(self, partyname)._trigger_gather()
            for indiv in getattr(self, partyname).elements:
                if indiv not in output_list:
                    output_list.append(indiv)
        return(output_list)

# class Jurisdiction(DAObject):
#     """Represents a jurisdiction, e.g. of a Court.  No functionality
#     implemented yet."""
#     pass

class Document(DAObject):
    """This is a base class for different types of documents."""
    def init(self, *pargs, **kwargs):
        return super().init(*pargs, **kwargs)
    def __str__(self):
        return str(self.title)

class LegalFiling(Document):
    """Represents a document filed in court."""
    def caption(self):
        """Returns a case caption for the case, for inclusion in documents."""
        #logmessage("caption: gathering first party")
        #logmessage("caption: case action_type is " + self.case.action_type)
        #logmessage("caption: case instanceName is " + self.case.instanceName)
        #logmessage("caption: instanceName is " + self.case.firstParty.instanceName)
        self.case.firstParty.gather()
        #logmessage("caption: gathered first party")
        if not self.case.is_solo_action:
            #logmessage("caption: case is solo action")
            self.case.secondParty.gather()
        output = ""
        #logmessage("caption: going to call in_the_court")
        output += "[BOLDCENTER] " + self.case.court.in_the_court(legalfiling=self, case=self.case) + "\n\n"
        output += "[BEGIN_CAPTION]"
        if self.case.action_type == 'in re':
            output += 'In re '
        output += comma_and_list(self.case.firstParty.elements, comma_string=",[NEWLINE]", and_string=word('and'), before_and=" ", after_and='[NEWLINE]') + ",[NEWLINE]"
        if self.case.action_type != 'in re':
            output += "[TAB][TAB]" + word(self.case.firstParty.as_noun()).capitalize() + "[NEWLINE] "
        if not self.case.is_solo_action:
            output += "[SKIPLINE][TAB]" + word('v.') + " [NEWLINE][SKIPLINE] "
            output += comma_and_list(self.case.secondParty.elements, comma_string=",[NEWLINE]", and_string=word('and'), before_and=" ", after_and='[NEWLINE]') + ",[NEWLINE]"
            output += "[TAB][TAB]" + word(self.case.secondParty.as_noun()).capitalize()
        output += "[VERTICAL_LINE]"
        output += self.case.case_id_in_caption(legalfiling=self)
        output += "[END_CAPTION]\n\n"
        if self.title is not None:
            output += "[BOLDCENTER] " + self.title.upper() + "\n"
        return(output)

class PartyList(DAList):
    """Represents a list of parties to a case.  The default object
    type for items in the list is Individual."""
    def init(self, *pargs, **kwargs):
        self.object_type = Individual
        return super().init(*pargs, **kwargs)

def us_districts(bankruptcy=False):
    if bankruptcy:
        return ['Northern District of Alabama', 'Middle District of Alabama', 'Southern District of Alabama', 'District of Alaska', 'District of Arizona', 'Eastern & Western Districts of Arkansas', 'Central District of California', 'Eastern District of California', 'Northern District of California', 'Southern District of California', 'District of Colorado', 'District of Connecticut', 'District of Delaware', 'District of Columbia', 'Northern District of Florida', 'Middle District of Florida', 'Southern District of Florida', 'Northern District of Georgia', 'Middle District of Georgia', 'Southern District of Georgia', 'District of Guam', 'District of Hawaii', 'District of Idaho', 'Northern District of Illinois', 'Central District of Illinois', 'Southern District of Illinois', 'Northern District of Indiana', 'Southern District of Indiana', 'Northern District of Iowa', 'Southern District of Iowa', 'District of Kansas', 'Eastern District of Kentucky', 'Western District of Kentucky', 'Eastern District of Louisiana', 'Middle District of Louisiana', 'Western District of Louisiana', 'District of Maine', 'District of Maryland', 'District of Massachusetts', 'Eastern District of Michigan', 'Western District of Michigan', 'District of Minnesota', 'Northern District of Mississippi', 'Southern District of Mississippi', 'Eastern District of Missouri', 'Western District of Missouri', 'District of Montana', 'District of Nebraska', 'District of Nevada', 'District of New Hampshire', 'District of New Jersey', 'District of New Mexico', 'Eastern District of New York', 'Northern District of New York', 'Southern District of New York', 'Western District of New York', 'Eastern District of North Carolina', 'Middle District of North Carolina', 'Western District of North Carolina', 'District of North Dakota', 'District of the Northern Mariana Islands', 'Northern District of Ohio', 'Southern District of Ohio', 'Eastern District of Oklahoma', 'Northern District of Oklahoma', 'Western District of Oklahoma', 'District of Oregon', 'Eastern District of Pennsylvania', 'Middle District of Pennsylvania', 'Western District of Pennsylvania', 'District of Puerto Rico', 'District of Rhode Island', 'District of South Carolina', 'District of South Dakota', 'Eastern District of Tennessee', 'Middle District of Tennessee', 'Western District of Tennessee', 'Eastern District of Texas', 'Northern District of Texas', 'Southern District of Texas', 'Western District of Texas', 'District of Utah', 'District of Vermont', 'District of the Virgin Islands', 'Eastern District of Virginia', 'Western District of Virginia', 'Eastern District of Washington', 'Western District of Washington', 'Northern District of West Virginia', 'Southern District of West Virginia', 'Eastern District of Wisconsin', 'Western District of Wisconsin', 'District of Wyoming']
    else:
        return ['Northern District of Alabama', 'Middle District of Alabama', 'Southern District of Alabama', 'District of Alaska', 'District of Arizona', 'Eastern District of Arkansas', 'Western District of Arkansas', 'Central District of California', 'Eastern District of California', 'Northern District of California', 'Southern District of California', 'District of Colorado', 'District of Connecticut', 'District of Delaware', 'District of Columbia', 'Northern District of Florida', 'Middle District of Florida', 'Southern District of Florida', 'Northern District of Georgia', 'Middle District of Georgia', 'Southern District of Georgia', 'District of Guam', 'District of Hawaii', 'District of Idaho', 'Northern District of Illinois', 'Central District of Illinois', 'Southern District of Illinois', 'Northern District of Indiana', 'Southern District of Indiana', 'Northern District of Iowa', 'Southern District of Iowa', 'District of Kansas', 'Eastern District of Kentucky', 'Western District of Kentucky', 'Eastern District of Louisiana', 'Middle District of Louisiana', 'Western District of Louisiana', 'District of Maine', 'District of Maryland', 'District of Massachusetts', 'Eastern District of Michigan', 'Western District of Michigan', 'District of Minnesota', 'Northern District of Mississippi', 'Southern District of Mississippi', 'Eastern District of Missouri', 'Western District of Missouri', 'District of Montana', 'District of Nebraska', 'District of Nevada', 'District of New Hampshire', 'District of New Jersey', 'District of New Mexico', 'Eastern District of New York', 'Northern District of New York', 'Southern District of New York', 'Western District of New York', 'Eastern District of North Carolina', 'Middle District of North Carolina', 'Western District of North Carolina', 'District of North Dakota', 'District of the Northern Mariana Islands', 'Northern District of Ohio', 'Southern District of Ohio', 'Eastern District of Oklahoma', 'Northern District of Oklahoma', 'Western District of Oklahoma', 'District of Oregon', 'Eastern District of Pennsylvania', 'Middle District of Pennsylvania', 'Western District of Pennsylvania', 'District of Puerto Rico', 'District of Rhode Island', 'District of South Carolina', 'District of South Dakota', 'Eastern District of Tennessee', 'Middle District of Tennessee', 'Western District of Tennessee', 'Eastern District of Texas', 'Northern District of Texas', 'Southern District of Texas', 'Western District of Texas', 'District of Utah', 'District of Vermont', 'District of the Virgin Islands', 'Eastern District of Virginia', 'Western District of Virginia', 'Eastern District of Washington', 'Western District of Washington', 'Northern District of West Virginia', 'Southern District of West Virginia', 'Eastern District of Wisconsin', 'Western District of Wisconsin', 'District of Wyoming']
