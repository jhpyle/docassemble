import docassemble.base.parse
import sys
import threading
import thread
from docassemble.base.logger import logmessage

_interview_cache = dict()

class ThreadVariables(threading.local):
    cache = dict()

this_thread = ThreadVariables()

def get_interview(path):
    if path is None:
        sys.exit("Tried to load interview source with no path")
    if cache_valid(path):
        #logmessage("get_interview: " + str(thread.get_ident()) + " cache is valid" + "\n")
        the_interview = this_thread.cache[path]['interview']
        # the_interview = _interview_cache[path]['interview']
        the_interview.from_cache = True
    else:
        #logmessage("get_interview: " + str(thread.get_ident()) + " fetching from cache" + "\n")
        interview_source = docassemble.base.parse.interview_source_from_string(path)
        interview_source.update()
        #modtime = interview_source.get_modtime()
        # if interview_source.path in _interview_cache:
        #     del _interview_cache[interview_source.path]
        the_interview = interview_source.get_interview()
        the_interview.from_cache = False
        #_interview_cache[interview_source.path] = {'modtime': modtime, 'interview': the_interview, 'source': interview_source}
        this_thread.cache[interview_source.path] = {'index': interview_source.get_index(), 'interview': the_interview, 'source': interview_source}
    return(the_interview)

def clear_cache(path):
    # if path in _interview_cache:
    #     del _interview_cache[path]
    if path in this_thread.cache:
        del this_thread.cache[path]

def cache_valid(questionPath):
    # if questionPath in _interview_cache and _interview_cache[questionPath]['modtime'] == _interview_cache[questionPath]['source'].get_modtime():
    #     return True
    # return False
    if questionPath in this_thread.cache and this_thread.cache[questionPath]['index'] == this_thread.cache[questionPath]['source'].get_index():
        return True
    return False
    #     return True
    # return False
    
