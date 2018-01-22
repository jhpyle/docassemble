import docassemble.base.parse
import sys
import threading
import thread

# from docassemble.base.logger import logmessage

# _interview_cache = dict()

class ThreadVariables(threading.local):
    cache = dict()

this_thread = ThreadVariables()

def get_interview(path):
    if path is None:
        sys.exit("Tried to load interview source with no path")
    # logmessage("get_interview: " + str(thread.get_ident()) + " checking cache" + "\n")
    if cache_valid(path):
        # logmessage("get_interview: " + str(thread.get_ident()) + " cache is valid" + "\n")
        the_interview = this_thread.cache[path]['interview']
        # the_interview = _interview_cache[path]['interview']
        the_interview.from_cache = True
    else:
        # sys.stderr.write("get_interview: " + str(thread.get_ident()) + " cache is not valid\n")
        # if path in this_thread.cache:
        #     sys.stderr.write("get_interview: had been cached with indexno " + this_thread.cache[path]['index'] + "\n")
        # else:
        #     sys.stderr.write("get_interview: had never been cached\n")
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
    # sys.stderr.write("clear_cache: " + str(thread.get_ident()) + " cache being cleared\n")
    if path in this_thread.cache:
        del this_thread.cache[path]

def cache_valid(questionPath):
    # if questionPath in _interview_cache and _interview_cache[questionPath]['modtime'] == _interview_cache[questionPath]['source'].get_modtime():
    #     return True
    # return False
    # if questionPath in this_thread.cache:
    #     logmessage("cache_valid: index is " + str(this_thread.cache[questionPath]['index']))
    # else:
    #     logmessage("cache_valid: index is unknown")
    if questionPath in this_thread.cache and this_thread.cache[questionPath]['index'] == this_thread.cache[questionPath]['source'].get_index():
        return True
    return False
    #     return True
    # return False
    
