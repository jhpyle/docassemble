class DAError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MandatoryQuestion(Exception):
    def __init__(self):
        self.value = 'Mandatory Question'
    def __str__(self):
        return repr(self.value)
