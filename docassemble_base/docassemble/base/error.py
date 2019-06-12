import re
from six import string_types, text_type

valid_variable_match = re.compile(r'^[^\d][A-Za-z0-9\_]*$')

class DAIndexError(IndexError):
    pass

class DAAttributeError(AttributeError):
    pass

class DAError(Exception):
    def __init__(self, value, code=501):
        self.value = value
        self.error_code = code
    def __str__(self):
        return text_type(self.value)

class DAValidationError(Exception):
    """This is an Exception object that is used when raising an exception inside input validation code."""
    pass

class CodeExecute(Exception):
    def __init__(self, compute, question):
        if type(compute) is list:
            self.compute = "\n".join(compute)
        else:
            self.compute = compute
        self.question = question

class ForcedReRun(Exception):
    pass

class LazyNameError(NameError):
    pass

def invalid_variable_name(varname):
    if not isinstance(varname, string_types):
        return True
    if re.search(r'[\n\r\(\)\{\}\*\^\#]', varname):
        return True
    varname = re.sub(r'[\.\[].*', '', varname)
    if not valid_variable_match.match(varname):
        return True
    return False

class ForcedNameError(NameError):
    def __init__(self, *pargs, **kwargs):
        the_args = [x for x in pargs]
        if len(the_args) == 0:
            raise DAError("ForcedNameError must have at least one argument")
        the_context = dict()
        the_user_dict = kwargs.get('user_dict', dict())
        for var_name in ('x', 'i', 'j', 'k', 'l', 'm', 'n'):
            if var_name in the_user_dict:
                the_context[var_name] = the_user_dict[var_name]
        if type(the_args[0]) is dict:
            if 'action' in the_args[0] and (len(the_args[0]) == 1 or 'arguments' in the_args[0]):
                self.name = the_args[0]['action']
                self.arguments = the_args[0].get('arguments', dict())
                self.context = the_context
        else:
            self.name = the_args[0]
            self.arguments = None
            self.context = the_context
        if kwargs.get('gathering', False):
            self.next_action = None
            return
        self.next_action = list()
        while len(the_args):
            arg = the_args.pop(0)
            if type(arg) is dict:
                if (len(arg.keys()) == 2 and 'action' in arg and 'arguments' in arg) or (len(arg.keys()) == 1 and 'action' in arg):
                    self.set_action(arg)
                elif len(arg) == 1 and ('undefine' in arg or 'recompute' in arg or 'set' in arg or 'follow up' in arg):
                    if 'set' in arg:
                        if type(arg['set']) is not list:
                            raise DAError("force_ask: the set statement must refer to a list.")
                        clean_list = []
                        for the_dict in arg['set']:
                            if type(the_dict) is not dict:
                                raise DAError("force_ask: a set command must refer to a list of dicts.")
                            for the_var, the_val in the_dict.items():
                                if not isinstance(the_var, string_types):
                                    raise DAError("force_ask: a set command must refer to a list of dicts with keys as variable names.  ")
                                the_var_stripped = the_var.strip()
                            if invalid_variable_name(the_var_stripped):
                                raise DAError("force_ask: missing or invalid variable name " + repr(the_var) + ".")
                            clean_list.append([the_var_stripped, the_val])
                        self.set_action(dict(action='_da_set', arguments=dict(variables=clean_list), context=the_context))
                    if 'follow up' in arg:
                        if type(arg['follow up']) is not list:
                            raise DAError("force_ask: the follow up statement must refer to a list.")
                        for var in arg['follow up']:
                            if not isinstance(var, string_types):
                                raise DAError("force_ask: invalid variable name " + repr(var) + " in follow up.")
                            var_saveas = var.strip()
                            if invalid_variable_name(var_saveas):
                                raise DAError("force_ask: missing or invalid variable name " + repr(var_saveas) + " .  " + repr(data))
                            self.set_action(dict(action=var, arguments=dict(), context=the_context))
                    for command in ('undefine', 'recompute'):
                        if command not in arg:
                            continue
                        if type(arg[command]) is not list:
                            raise DAError("force_ask: the " + command + " statement must refer to a list.  " + repr(data))
                        clean_list = []
                        for undef_var in arg[command]:
                            if not isinstance(undef_var, string_types):
                                raise DAError("force_ask: invalid variable name " + repr(undef_var) + " in " + command + ".  " + repr(data))
                            undef_saveas = undef_var.strip()
                            if invalid_variable_name(undef_saveas):
                                raise DAError("force_ask: missing or invalid variable name " + repr(undef_saveas) + " .  " + repr(data))
                            clean_list.append(undef_saveas)
                        self.next_action.append(dict(action='_da_undefine', arguments=dict(variables=clean_list), context=the_context))
                        if command == 'recompute':
                            self.set_action(dict(action='_da_compute', arguments=dict(variables=clean_list), context=the_context))
                else:
                    raise DAError("Dictionaries passed to force_ask must have keys of 'action' and 'argument' only.")
            else:
                self.set_action(dict(action=arg, arguments=dict(), context=the_context))
    def set_action(self, data):
        if not hasattr(self, 'name'):
            if isinstance(data, dict) and 'action' in data and (len(data) == 1 or 'arguments' in data):
                self.name = data['action']
                self.arguments = data.get('arguments', dict())
                self.context = data.get('context', dict())
            else:
                raise DAError("force_ask: invalid parameter " + repr(data))
        self.next_action.append(data)

class DAErrorNoEndpoint(DAError):
    pass

class DAErrorMissingVariable(DAError):
    def __init__(self, value, variable=None, code=501):
        self.value = value
        self.variable = variable
        self.error_code = code

class DAErrorCompileError(DAError):
    pass

class MandatoryQuestion(Exception):
    def __init__(self):
        self.value = 'Mandatory Question'
    def __str__(self):
        return text_type(self.value)

class QuestionError(Exception):
    def __init__(self, *pargs, **kwargs):
        if len(pargs) >= 1:
            self.question = pargs[0];
        elif 'question' in kwargs:
            self.question = kwargs['question'];
        else:
            self.question = "Question not specified"
        if len(pargs) >= 2:
            self.subquestion = pargs[1];
        elif 'subquestion' in kwargs:
            self.subquestion = kwargs['subquestion'];
        else:
            self.subquestion = None
        if len(pargs) >= 3:
            self.url = pargs[2];
        elif 'url' in kwargs:
            self.url = kwargs['url'];
        else:
            self.url = None
        if 'show_leave' in kwargs:
            self.show_leave = kwargs['show_leave'];
        else:
            self.show_leave = None
        if 'show_exit' in kwargs:
            self.show_exit = kwargs['show_exit'];
        else:
            self.show_exit = None
        if 'show_restart' in kwargs:
            self.show_restart = kwargs['show_restart'];
        else:
            self.show_restart = None
        if 'buttons' in kwargs:
            self.buttons = kwargs['buttons']
        else:
            self.buttons = None
        if 'dead_end' in kwargs:
            self.dead_end = kwargs['dead_end']
        else:
            self.dead_end = None
    def __str__(self):
        return str(self.question)

class BackgroundResponseError(Exception):
    def __init__(self, *pargs, **kwargs):
        if len(pargs) > 0 and len(kwargs) > 0:
            self.backgroundresponse = dict(pargs=[arg for arg in pargs], kwargs=kwargs)
        elif len(pargs) > 1:
            self.backgroundresponse = [arg for arg in pargs]
        elif len(pargs) == 1:
            self.backgroundresponse = pargs[0]
        else:
            self.backgroundresponse = kwargs
    def __str__(self):
        if hasattr(self, 'backgroundresponse'):
            return str(self.backgroundresponse)
        return "A BackgroundResponseError exception was thrown"

class BackgroundResponseActionError(Exception):
    def __init__(self, *pargs, **kwargs):
        self.action = dict(arguments=dict())
        if len(pargs) == 0:
            self.action['action'] = None
        else:
            self.action['action'] = pargs[0]
        for key in kwargs:
            self.action['arguments'][key] = kwargs[key]
    def __str__(self):
        if hasattr(self, 'action'):
            return str(self.action)
        return "A BackgroundResponseActionError exception was thrown"

class ResponseError(Exception):
    def __init__(self, *pargs, **kwargs):
        if len(pargs) == 0 and not ('response' in kwargs or 'binaryresponse' in kwargs or 'all_variables' in kwargs or 'file' in kwargs or 'url' in kwargs or 'null' in kwargs):
            self.response = "Empty Response"
        if len(pargs) > 0:
            self.response = pargs[0];
        elif 'response' in kwargs:
            self.response = kwargs['response'];
        elif 'binaryresponse' in kwargs:
            self.binaryresponse = kwargs['binaryresponse'];
        elif 'file' in kwargs:
            self.filename = kwargs['file'];
        elif 'url' in kwargs:
            self.url = kwargs['url'];
        elif 'null' in kwargs:
            self.nullresponse = kwargs['null'];
        if 'all_variables' in kwargs:
            self.all_variables = kwargs['all_variables'];
            if 'include_internal' in kwargs:
                self.include_internal = kwargs['include_internal']
        if 'content_type' in kwargs:
            self.content_type = kwargs['content_type'];
    def __str__(self):
        if hasattr(self, 'response'):
            return str(self.response)
        return "A ResponseError exception was thrown"

class CommandError(Exception):
    def __init__(self, *pargs, **kwargs):
        if len(pargs) > 0:
            self.return_type = pargs[0];
        elif 'type' in kwargs:
            self.return_type = kwargs['type'];
        else:
            self.return_type = "exit"
        self.url = kwargs.get('url', '');
    def __str__(self):
        return str(self.return_type)
