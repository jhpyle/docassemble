from docassemble.base.util import DAObject, DAList, DAFileCollection, interview_url_action, DADict, word, message, noun_singular, noun_plural, today, current_datetime, Person, DAEmailRecipient, comma_and_list, interface, value, send_email, background_action, reconsider, force_ask, background_response, device
import random
import string

__all__ = ['SigningProcess']

class SigningProcess(DAObject):
    def init(self, *pargs, **kwargs):
        self.deadline_days = 30
        self.additional_people_to_notify = []
        super().init(*pargs, **kwargs)
        self.initializeAttribute('initial_notification_email', DADict)
        self.initializeAttribute('final_notification_email', DADict)
        self.initializeAttribute('willing_to_sign', DADict)
        self.initializeAttribute('signature', DADict)
        self.initializeAttribute('blank_signature_date', DADict)
        self.initializeAttribute('blank_signature_datetime', DADict)
        self.initializeAttribute('blank_signature', DADict)
        self.initializeAttribute('thank_you_screen', DADict)
        self.info_by_code = dict()
        self.initial_notification_triggered = False
        self.initial_notification_sent = False
        self.final_notification_triggered = False
        self.final_notification_sent = False
    def rationalize(self):
        if not isinstance(self.documents, (list, DAList)):
            self.documents = [self.documents]
        for document in self.documents:
            if not isinstance(document, str):
                raise Exception("SigningProcess.notify: the document references must consist of text strings only")
            if not isinstance(value(document), DAFileCollection):
                raise Exception("SigningProcess.notify: the document references must refer to DAFileCollection objects only")
        if not isinstance(self.additional_people_to_notify, (list, DAList)):
            self.additional_people_to_notify = [self.additional_people_to_notify]
        for person in self.additional_people_to_notify:
            if not isinstance(person, (Person, DAEmailRecipient)):
                raise Exception("SigningProcess: an additional person to notify must be a person")
    def out_for_signature(self):
        if self.initial_notification_triggered or self.initial_notification_sent:
            return
        self.rationalize()
        for code, info in self.info_by_code.items():
            if not info['signed']:
                send_email(to=info['signer'], template=self.initial_notification_email[code], dry_run=True)
            send_email(to=info['signer'], template=self.final_notification_email[code], dry_run=True)
        for person in self.additional_people_to_notify:
            send_email(to=person, template=self.final_notification_email_to_others, dry_run=True)
        background_action(self.attr_name('background_initial_notification'))
        self.initial_notification_triggered = True
    def initial_notify(self):
        if self.initial_notification_sent:
            return
        self.rationalize()
        for code, info in self.info_by_code.items():
            if not info['signed']:
                str(self.initial_notification_email[code])
        if len(self.additional_people_to_notify):
            str(self.final_notification_email_to_others)
        for code, info in self.info_by_code.items():
            if not info['signed']:
                send_email(to=info['signer'], template=self.initial_notification_email[code])
        for person in self.additional_people_to_notify:
            send_email(to=person, template=self.final_notification_email_to_others)
        self.initial_notification_sent = True
        if interface() == 'worker':
            background_response()
    def sign_for(self, signer, signature):
        code = _code_for(self, signer)
        if self.info_by_code[code]['signed']:
            return
        self.signature[code] = signature
        self.validate_signature(code)
    def refresh_documents(self):
        reconsider(*[y for y in self.documents])
    def final_notify(self):
        if self.final_notification_sent:
            return
        self.refresh_documents()
        for code, info in self.info_by_code.items():
            str(self.final_notification_email[code])
        if len(self.additional_people_to_notify):
            str(self.final_notification_email_to_others)
        for code, info in self.info_by_code.items():
            send_email(to=info['signer'], template=self.final_notification_email[code], attachments=self.list_of_documents())
        for person in self.additional_people_to_notify:
            send_email(to=person, template=self.final_notification_email_to_others, attachments=self.list_of_documents())
        self.final_notification_sent = True
        if interface() == 'worker':
            background_response()
    def _verify_signer(self, signer):
        if not isinstance(signer, Person):
            if hasattr(signer, 'instanceName'):
                raise Exception("There was a reference to a signer " + signer.instanceName + " that is not a person.")
            raise Exception("There was a reference to a signer that is not a person.")
        if signer not in [y['signer'] for y in self.info_by_code.values()]:
            code = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            self.info_by_code[code] = dict(signed=False, signer=signer)
    def _code_for(self, signer):
        self._verify_signer(signer)
        for code, info in self.info_by_code.items():
            if info['signer'] is signer:
                return code
        raise Exception("No code existed for signer")
    def has_signed(self, signer):
        code = self._code_for(signer)
        return self.info_by_code[code]['signed']
    def signature_of(self, signer):
        code = self._code_for(signer)
        if self.info_by_code[code]['signed']:
            return self.signature[code]
        else:
            return self.blank_signature[code]
    def signature_date_of(self, signer):
        code = self._code_for(signer)
        if self.info_by_code[code]['signed']:
            return self.info_by_code[code]['date']
        else:
            return self.blank_signature_date[code]
    def signature_datetime_of(self, signer):
        code = self._code_for(signer)
        if self.info_by_code[code]['signed']:
            return self.info_by_code[code]['datetime']
        else:
            return self.blank_signature_datetime[code]
    def signature_ip_address_of(self, signer):
        code = self._code_for(signer)
        if self.info_by_code[code]['signed']:
            return self.info_by_code[code]['ip']
        else:
            return self.blank_ip_address[code]
    def collect_signature(self, code):
        if code is None or code not in self.info_by_code:
            force_ask(self.attr_name('unauthorized_screen'))
        info = self.info_by_code[code]
        index_part = '[' + repr(code) + ']'
        if self.info_by_code[code]['signed']:
            force_ask(self.attr_name('thank_you_screen') + index_part)
        force_ask(self.attr_name('willing_to_sign') + index_part,
                  self.attr_name('signature') + index_part,
                  self.attr_name('thank_you_screen') + index_part)
    def validate_signature(self, code):
        if code not in self.info_by_code:
            raise Exception("Invalid code")
        self.info_by_code[code]['signed'] = True
        self.info_by_code[code]['date'] = today()
        self.info_by_code[code]['datetime'] = current_datetime()
        self.info_by_code[code]['ip'] = device(ip=True) or word("Unable to determine IP address")
        self.check_if_final()
    def check_if_final(self):
        if self.final_notification_triggered or self.final_notification_sent:
            return
        if self.all_signatures_in():
            background_action(self.attr_name('background_final_notification'))
            self.final_notification_triggered = True
    def signer(self, code):
        if code is None:
            return None
        if code in self.info_by_code:
            return self.info_by_code[code]['signer']
        return None
    def url(self, code):
        return interview_url_action(self.attr_name('request_signature'), code=code, temporary=24 * self.deadline_days)
    def list_of_documents(self, refresh=False):
        self.rationalize()
        if refresh:
            self.refresh_documents()
        return [value(y) for y in self.documents]
    def number_of_documents(self):
        return len(self.documents)
    def singular_or_plural(self, singular_word, plural_word):
        return singular_word if self.number_of_documents() == 1 else plural_word
    def documents_name(self):
        return comma_and_list([y.info['name'] for y in self.list_of_documents()])
    def all_signatures_in(self):
        return all(y['signed'] for y in self.info_by_code.values())
    def list_of_signers(self):
        result = DAList()
        result.set_random_instance_name()
        for code, info in self.info_by_code.items():
            result.append(info['signer'])
        return result
    def signers_who_signed(self):
        result = DAList()
        result.set_random_instance_name()
        for code, info in self.info_by_code.items():
            if info['signed']:
                result.append(info['signer'])
        return result
    def signers_who_did_not_sign(self):
        result = DAList()
        result.set_random_instance_name()
        for code, info in self.info_by_code.items():
            if not info['signed']:
                result.append(info['signer'])
        return result
    def number_of_signers(self):
        return len(self.info_by_code)
