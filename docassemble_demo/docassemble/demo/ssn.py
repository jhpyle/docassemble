from docassemble.base.util import CustomDataType, DAValidationError, word
import re

class SSN(CustomDataType):
    name = 'ssn'
    container_class = 'da-ssn-container'
    input_class = 'da-ssn'
    javascript = """\
$.validator.addMethod('ssn', function(value, element, params){
  return value == '' || /^[0-9]{3}\-?[0-9]{2}\-?[0-9]{4}$/.test(value);
});
"""
    jq_rule = 'ssn'
    jq_message = 'You need to enter a valid SSN.'
    @classmethod
    def validate(cls, item):
        item = str(item).strip()
        m = re.search(r'^[0-9]{3}-?[0-9]{2}-?[0-9]{4}$', item)
        if item == '' or m:
            return True
        raise DAValidationError("A SSN needs to be in the form xxx-xx-xxxx")
    @classmethod
    def transform(cls, item):
        item = str(item).strip()
        m = re.search(r'^([0-9]{3})-?([0-9]{2})-?([0-9]{4})$', item)
        if m:
            return m.group(1) + '-' + m.group(2) + '-' + m.group(3)
        else:
            return item
