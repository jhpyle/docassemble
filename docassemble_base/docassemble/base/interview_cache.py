import docassemble.base.parse
import sys
#from docassemble.logger import logmessage

_interview_cache = dict()

def get_interview(path):
    if path is None:
        sys.exit("Tried to load interview source with no path")
    if cache_valid(path):
        #logmessage("Cache is valid" + "\n")
        the_interview = _interview_cache[path]['interview']
    else:
        #logmessage("Not fetching from cache" + "\n")
        interview_source = docassemble.base.parse.interview_source_from_string(path)
        interview_source.update()
        modtime = interview_source.get_modtime()
        if interview_source.path in _interview_cache:
            del _interview_cache[interview_source.path]
        the_interview = interview_source.get_interview()
        _interview_cache[interview_source.path] = {'modtime': modtime, 'interview': the_interview, 'source': interview_source}
    return(the_interview)

def clear_cache(path):
    if path in _interview_cache:
        del _interview_cache[path]

def cache_valid(questionPath):
    if questionPath in _interview_cache and _interview_cache[questionPath]['modtime'] == _interview_cache[questionPath]['source'].get_modtime():
        return True
    return False
