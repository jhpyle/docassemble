import string
import random
from docassemble.base.util import possessify, possessify_long, a_in_the_b, your, the, underscore_to_space
#from docassemble.logger import logmessage

unique_names = set()

def get_unique_name():
    while True:
        newname = ''.join(random.choice(string.ascii_letters) for i in range(12))
        if newname in unique_names:
            continue
        unique_names.add(newname)
        return newname

class DAObject(object):
    def init(self):
        return
    def __init__(self, *args, **kwargs):
        if len(args):
            thename = args[0]
        else:
            thename = get_unique_name()
        self.instanceName = thename
        #logmessage("Initialized " + thename + "\n")
        self.init(**kwargs)
    def __getattr__(self, thename):
        if hasattr(self, thename) or thename == "__getstate__" or thename == "__slots__":
            return(object.__getattribute__(self, thename))
        else:
            raise NameError("Undefined name '" + object.__getattribute__(self, 'instanceName') + "." + thename + "'")
    def object_name(self):
        return(reduce(a_in_the_b, map(underscore_to_space, reversed(self.instanceName.split(".")))))
    def object_possessive(self, target):
        if self.instanceName == 'user':
            return(your(target))
        if len(self.instanceName.split(".")) > 1:
            return(possessify_long(self.object_name(), target))
        else:
            return(possessify(the(self.object_name()), target))
    def initializeAttribute(self, name, objectType):
        if name in self.__dict__:
            return
        else:
            object.__setattr__(self, name, objectType(self.instanceName + "." + name))

