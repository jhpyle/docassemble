class DAError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class DAErrorNoEndpoint(DAError):
    pass

class DAErrorMissingVariable(DAError):
    pass

class MandatoryQuestion(Exception):
    def __init__(self):
        self.value = 'Mandatory Question'
    def __str__(self):
        return str(self.value)

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
