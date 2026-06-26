from docassemble.base.error import DAException
from docassemble.base.interview_source import interview_source_from_string
from docassemble.base.parse import Interview

cache = {}

def get_interview(path):
    if path is None:
        raise DAException("Tried to load interview source with no path")
    if cache_valid(path):
        the_interview = cache[path]['interview']
        the_interview.from_cache = True
    else:
        interview_source = interview_source_from_string(path)
        interview_source.update()
        the_interview = Interview(source=interview_source)
        the_interview.from_cache = False
        cache[interview_source.path] = {'index': interview_source.get_index(), 'interview': the_interview, 'source': interview_source}
    return the_interview


def clear_cache(path):
    if path in cache:
        del cache[path]


def cache_valid(question_path):
    if question_path in cache and cache[question_path]['index'] == cache[question_path]['source'].get_index():
        return True
    return False
