import re


valid_variable_match = re.compile(r'^[^\d][A-Za-z0-9\_]*$')
match_brackets_or_dot = re.compile(r'(\[.+?\]|\.[a-zA-Z_][a-zA-Z0-9_]*)')

class DAIndexError(IndexError):
    pass


class DAAttributeError(AttributeError):
    pass


class DAException(Exception):
    pass


class DAError(Exception):

    def __init__(self, value, code=501):
        self.value = value
        self.error_code = code
        super().__init__(value)

    def __str__(self):
        return str(self.value)


class DASourceError(DAError):
    pass

class DANotFoundError(Exception):
    pass


class DAInvalidFilename(Exception):
    pass


class DAValidationError(Exception):
    """This is an Exception object that is used when raising an exception inside input validation code."""

    def __init__(self, *pargs, field=None):
        self.field = field
        super().__init__(*pargs)


class CodeExecute(Exception):

    def __init__(self, compute, question):
        if isinstance(compute, list):
            self.compute = "\n".join(compute)
        else:
            self.compute = compute
        self.question = question
        super().__init__()


class ForcedReRun(Exception):
    pass


class LazyNameError(NameError):
    pass


class DANameError(NameError):
    pass


def invalid_variable_name(varname):
    if not isinstance(varname, str):
        return True
    if re.search(r'[\n\r\(\)\{\}\*\^\#]', varname):
        return True
    varname = re.sub(r'[\.\[].*', '', varname)
    if not valid_variable_match.match(varname):
        return True
    return False


def intrinsic_name_of(var_name, the_user_dict):
    from docassemble.base.util import DAObject  # pylint: disable=import-outside-toplevel
    expression_as_list = [x for x in match_brackets_or_dot.split(var_name) if x != '']
    n = len(expression_as_list)
    i = n
    while i > 0:
        try:
            item = eval(var_name, the_user_dict)
            if isinstance(item, DAObject) and item.has_nonrandom_instance_name:
                var_name = item.instanceName
                break
        except:
            pass
        i -= 1
        var_name = ''.join(expression_as_list[0:i])
    return var_name + (''.join(expression_as_list[i:n]))


class ForcedNameError(NameError):

    def __init__(self, *pargs, **kwargs):
        super().__init__()
        the_args = list(pargs)
        if len(the_args) == 0:
            raise DAError("ForcedNameError must have at least one argument")
        the_context = {}
        the_user_dict = kwargs.get('user_dict', {})
        for var_name in ('x', 'i', 'j', 'k', 'l', 'm', 'n'):
            if var_name in the_user_dict:
                the_context[var_name] = the_user_dict[var_name]
        first_is_plain = bool(isinstance(the_args[0], str))
        self.next_action = []
        evaluate = kwargs.get('evaluate', False)
        while len(the_args) > 0:
            arg = the_args.pop(0)
            if isinstance(arg, dict):
                if (len(arg.keys()) == 2 and 'action' in arg and 'arguments' in arg) or (len(arg.keys()) == 1 and 'action' in arg):
                    arg['context'] = the_context
                    self.set_action(arg)
                elif len(arg) == 1 and ('undefine' in arg or 'invalidate' in arg or 'recompute' in arg or 'set' in arg or 'follow up' in arg):
                    if 'set' in arg:
                        if isinstance(arg['set'], dict):
                            arg['set'] = [arg['set']]
                        if not isinstance(arg['set'], list):
                            raise DAError("force_ask: the set statement must refer to a list.")
                        clean_list = []
                        for the_dict in arg['set']:
                            if not isinstance(the_dict, dict):
                                raise DAError("force_ask: a set command must refer to a list of dicts.")
                            for the_var, the_val in the_dict.items():
                                if not isinstance(the_var, str):
                                    raise DAError("force_ask: a set command must refer to a list of dicts with keys as variable names.  ")
                                the_var_stripped = the_var.strip()
                                if invalid_variable_name(the_var_stripped):
                                    raise DAError("force_ask: missing or invalid variable name " + repr(the_var) + ".")
                                clean_list.append([the_var_stripped, the_val])
                        self.set_action({'action': '_da_set', 'arguments': {'variables': clean_list}, 'context': the_context})
                    if 'follow up' in arg:
                        if isinstance(arg['follow up'], str):
                            arg['follow up'] = [arg['follow up']]
                        if not isinstance(arg['follow up'], list):
                            raise DAError("force_ask: the follow up statement must refer to a list.")
                        for var in arg['follow up']:
                            if not isinstance(var, str):
                                raise DAError("force_ask: invalid variable name " + repr(var) + " in follow up.")
                            var_saveas = var.strip()
                            if invalid_variable_name(var_saveas):
                                raise DAError("force_ask: missing or invalid variable name " + repr(var_saveas) + ".")
                            if evaluate:
                                var = intrinsic_name_of(var, the_user_dict)
                            self.set_action({'action': var, 'arguments': {}, 'context': the_context})
                    for command in ('undefine', 'invalidate', 'recompute'):
                        if command not in arg:
                            continue
                        if isinstance(arg[command], str):
                            arg[command] = [arg[command]]
                        if not isinstance(arg[command], list):
                            raise DAError("force_ask: the " + command + " statement must refer to a list.  ")
                        clean_list = []
                        for undef_var in arg[command]:
                            if not isinstance(undef_var, str):
                                raise DAError("force_ask: invalid variable name " + repr(undef_var) + " in " + command + ".")
                            undef_saveas = undef_var.strip()
                            if invalid_variable_name(undef_saveas):
                                raise DAError("force_ask: missing or invalid variable name " + repr(undef_saveas) + ".")
                            if evaluate:
                                undef_saveas = intrinsic_name_of(undef_saveas, the_user_dict)
                            clean_list.append(undef_saveas)
                        if command == 'invalidate':
                            self.set_action({'action': '_da_invalidate', 'arguments': {'variables': clean_list}, 'context': the_context})
                        else:
                            self.set_action({'action': '_da_undefine', 'arguments': {'variables': clean_list}, 'context': the_context})
                        if command == 'recompute':
                            self.set_action({'action': '_da_compute', 'arguments': {'variables': clean_list}, 'context': the_context})
                else:
                    raise DAError("Dictionaries passed to force_ask must have keys of 'action' and 'argument' only.")
            else:
                if evaluate:
                    arg = intrinsic_name_of(arg, the_user_dict)
                self.set_action({'action': arg, 'arguments': {}, 'context': the_context})
        if kwargs.get('gathering', False):
            self.next_action = None
        if first_is_plain:
            self.arguments = None

    def set_action(self, data):
        if (not hasattr(self, 'name')) or self.name is None:
            if isinstance(data, dict) and 'action' in data and (len(data) == 1 or 'arguments' in data):
                self.name = data['action']
                self.arguments = data.get('arguments', {})
                self.context = data.get('context', {})
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
        super().__init__(value)


class DAErrorCompileError(DAError):
    pass


class MandatoryQuestion(Exception):

    def __init__(self):
        self.value = 'Mandatory Question'
        super().__init__()

    def __str__(self):
        return str(self.value)


class QuestionError(Exception):

    def __init__(self, *pargs, **kwargs):
        if len(pargs) >= 1:
            self.question = pargs[0]
        elif 'question' in kwargs:
            self.question = kwargs['question']
        else:
            self.question = "Question not specified"
        if len(pargs) >= 2:
            self.subquestion = pargs[1]
        elif 'subquestion' in kwargs:
            self.subquestion = kwargs['subquestion']
        else:
            self.subquestion = None
        if len(pargs) >= 3:
            self.url = pargs[2]
        elif 'url' in kwargs:
            self.url = kwargs['url']
        else:
            self.url = None
        if 'show_leave' in kwargs:
            self.show_leave = kwargs['show_leave']
        else:
            self.show_leave = None
        if 'show_exit' in kwargs:
            self.show_exit = kwargs['show_exit']
        else:
            self.show_exit = None
        if 'reload' in kwargs:
            self.reload = kwargs['reload']
        else:
            self.reload = None
        if 'show_restart' in kwargs:
            self.show_restart = kwargs['show_restart']
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
        super().__init__()

    def __str__(self):
        return str(self.question)


class BackgroundResponseError(Exception):

    def __init__(self, *pargs, **kwargs):
        if len(pargs) > 0 and len(kwargs) > 0:
            self.backgroundresponse = {'pargs': list(pargs), 'kwargs': kwargs}
        elif len(pargs) > 1:
            self.backgroundresponse = list(pargs)
        elif len(pargs) == 1:
            self.backgroundresponse = pargs[0]
        else:
            self.backgroundresponse = kwargs
        if 'sleep' in kwargs:
            self.sleep = kwargs['sleep']
        super().__init__()

    def __str__(self):
        if hasattr(self, 'backgroundresponse'):
            return str(self.backgroundresponse)
        return "A BackgroundResponseError exception was thrown"


class BackgroundResponseActionError(Exception):

    def __init__(self, *pargs, **kwargs):
        self.action = {'arguments': {}}
        if len(pargs) == 0:
            self.action['action'] = None
        else:
            self.action['action'] = pargs[0]
        for key, val in kwargs.items():
            self.action['arguments'][key] = val
        super().__init__()

    def __str__(self):
        if hasattr(self, 'action'):
            return str(self.action)
        return "A BackgroundResponseActionError exception was thrown"


class ResponseError(Exception):

    def __init__(self, *pargs, **kwargs):
        if len(pargs) == 0 and not ('response' in kwargs or 'binaryresponse' in kwargs or 'all_variables' in kwargs or 'file' in kwargs or 'url' in kwargs or 'null' in kwargs):
            self.response = "Empty Response"
        if len(pargs) > 0:
            self.response = pargs[0]
        elif 'response' in kwargs:
            self.response = kwargs['response']
        elif 'binaryresponse' in kwargs:
            self.binaryresponse = kwargs['binaryresponse']
        elif 'file' in kwargs:
            self.filename = kwargs['file']
        elif 'url' in kwargs:
            self.url = kwargs['url']
        elif 'null' in kwargs:
            self.nullresponse = kwargs['null']
        if 'response_code' in kwargs and kwargs['response_code'] is not None:
            self.response_code = kwargs['response_code']
        if 'sleep' in kwargs:
            self.sleep = kwargs['sleep']
        if 'all_variables' in kwargs:
            self.all_variables = kwargs['all_variables']
            if 'include_internal' in kwargs:
                self.include_internal = kwargs['include_internal']
        if 'content_type' in kwargs:
            self.content_type = kwargs['content_type']
        super().__init__()

    def __str__(self):
        if hasattr(self, 'response'):
            return str(self.response)
        return "A ResponseError exception was thrown"


class CommandError(Exception):

    def __init__(self, *pargs, **kwargs):
        if len(pargs) > 0:
            self.return_type = pargs[0]
        elif 'type' in kwargs:
            self.return_type = kwargs['type']
        else:
            self.return_type = "exit"
        self.url = kwargs.get('url', '')
        self.sleep = kwargs.get('sleep', None)
        super().__init__()

    def __str__(self):
        return str(self.return_type)


class DAWebError(Exception):

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        super().__init__()
