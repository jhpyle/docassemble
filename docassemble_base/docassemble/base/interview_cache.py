import docassemble.base.parse

cache = {}

def get_interview(path):
    if path is None:
        raise Exception("Tried to load interview source with no path")
    if cache_valid(path):
        the_interview = cache[path]['interview']
        the_interview.from_cache = True
    else:
        interview_source = docassemble.base.parse.interview_source_from_string(path)
        interview_source.update()
        the_interview = interview_source.get_interview()
        the_interview.from_cache = False
        cache[interview_source.path] = {'index': interview_source.get_index(), 'interview': the_interview, 'source': interview_source}
    return the_interview

def clear_cache(path):
    if path in cache:
        del cache[path]

def cache_valid(questionPath):
    if questionPath in cache and cache[questionPath]['index'] == cache[questionPath]['source'].get_index():
        return True
    return False
