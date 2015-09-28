import sys

def default_logmessage(message):
    sys.stderr.write(message + "\n")

the_logmessage = default_logmessage

def set_logmessage(func):
    global the_logmessage
    the_logmessage = func
    return

def logmessage(message):
    return the_logmessage(message)
    
