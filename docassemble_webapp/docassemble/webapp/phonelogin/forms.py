import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from flask import request, abort
from docassemble.base.language.words import LazyWord as word
from docassemble.base.logger import logmessage
from docassemble.webapp.config import daconfig, BAN_IP_ADDRESSES
from docassemble.webapp.daredis import r
from docassemble.webapp.services.validators import html_validator
from docassemble.webapp.utils.helpers import get_requester_ip

class PhoneLoginForm(FlaskForm):
    phone_number = StringField(word('Phone number'), [validators.Length(min=5, max=255), html_validator])
    submit = SubmitField(word('Go'))


class PhoneLoginVerifyForm(FlaskForm):
    phone_number = StringField(word('Phone number'), [validators.Length(min=5, max=255), html_validator])
    verification_code = StringField(word('Verification code'), [validators.Length(min=daconfig['verification code digits'], max=daconfig['verification code digits']), html_validator])
    submit = SubmitField(word('Verify'))

    def validate(self):  # pylint: disable=arguments-differ
        result = True
        if BAN_IP_ADDRESSES:
            key = 'da:failedlogin:ip:' + str(get_requester_ip(request))
            failed_attempts = r.get(key)
            if failed_attempts is not None and int(failed_attempts) > daconfig['attempt limit']:
                abort(404)
        verification_key = 'da:phonelogin:' + str(self.phone_number.data) + ':code'
        verification_code = r.get(verification_key)
        # r.delete(verification_key)
        supplied_verification_code = re.sub(r'[^0-9]', '', self.verification_code.data)
        logmessage("Supplied code is " + str(supplied_verification_code))
        if verification_code is None:
            logmessage("Verification code with " + str(verification_key) + " is None")
            result = False
        elif verification_code.decode() != supplied_verification_code:
            logmessage("Verification code with " + str(verification_key) + " which is " + str(verification_code.decode()) + " does not match supplied code, which is " + str(self.verification_code.data))
            result = False
        else:
            logmessage("Code matched")
        if result is False:
            logmessage("Problem with form")
            r.incr(key)
            r.expire(key, 86400)
        elif failed_attempts is not None:
            r.delete(key)
        return result
