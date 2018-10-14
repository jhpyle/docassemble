class DAError(Exception):
    def __init__(self, value, code=501):
        self.value = value
        self.error_code = code
    def __str__(self):
        return unicode(self.value)

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

class ForcedNameError(NameError):
    def __init__(self, *pargs, **kwargs):
        the_args = [x for x in pargs]
        #self.name = unicode(the_args.pop(0))
        if len(the_args) == 0:
            raise DAError("ForcedNameError must have at least one argument")
        if type(the_args[0]) is dict:
            self.name = the_args[0]['action']
            self.arguments = the_args[0]['arguments']
        else:
            self.name = the_args[0]
            self.arguments = None
        if kwargs.get('gathering', False):
            self.next_action = None
            return
        self.next_action = list()
        while len(the_args):
            arg = the_args.pop(0)
            if type(arg) is dict:
                if (len(arg.keys()) == 2 and 'action' in arg and 'arguments' in arg) or (len(arg.keys()) == 1 and 'action' in arg):
                    self.next_action.append(arg)
                else:
                    raise DAError("Dictionaries passed to force_ask must have keys of 'action' and 'argument' only.")
            else:
                self.next_action.append(dict(action=arg, arguments=dict()))

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
        return unicode(self.value)

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
        if len(pargs) == 0 and not ('response' in kwargs or 'binaryresponse' in kwargs or 'all_variables' in kwargs or 'file' in kwargs or 'url' in kwargs):
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

