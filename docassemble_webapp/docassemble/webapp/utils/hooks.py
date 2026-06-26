import re
from flask import url_for as base_url_for
from docassemble.base.functions import filename_invalid
from docassemble.base.hooks import write_ml_source
from docassemble.base.thread_context import this_thread
from docassemble.webapp.config import COOKIELESS_SESSIONS
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.users.common import user_is_developer

@hookimpl
def absolute_filename(the_file):
    match = re.match(r'^docassemble\.playground([0-9]+)([A-Za-z]?[A-Za-z0-9]*):(.*)', the_file)
    # logmessage("absolute_filename call: " + the_file)
    if match:
        if not user_is_developer(match.group(1)):
            return None
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(3))
        if filename_invalid(filename):
            return None
        # logmessage("absolute_filename: filename is " + filename + " and subdir is " + match.group(2))
        playground = SavedFile(match.group(1), section='playground', fix=True, filename=filename, subdir=match.group(2), must_exist=True)
        return playground
    match = re.match(r'^/playgroundtemplate/([0-9]+)/([A-Za-z0-9]+)/(.*)', the_file)
    if match:
        if not user_is_developer(match.group(1)):
            return None
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(3))
        if filename_invalid(filename):
            return None
        playground = SavedFile(match.group(1), section='playgroundtemplate', fix=True, filename=filename, subdir=match.group(2), must_exist=True)
        return playground
    match = re.match(r'^/playgroundstatic/([0-9]+)/([A-Za-z0-9]+)/(.*)', the_file)
    if match:
        if not user_is_developer(match.group(1)):
            return None
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(3))
        if filename_invalid(filename):
            return None
        playground = SavedFile(match.group(1), section='playgroundstatic', fix=True, filename=filename, subdir=match.group(2), must_exist=True)
        return playground
    match = re.match(r'^/playgroundsources/([0-9]+)/([A-Za-z0-9]+)/(.*)', the_file)
    if match:
        if not user_is_developer(match.group(1)):
            return None
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(3))
        if filename_invalid(filename):
            return None
        playground = SavedFile(match.group(1), section='playgroundsources', fix=True, filename=filename, subdir=match.group(2), must_exist=True)
        write_ml_source(playground, match.group(1), match.group(2), filename)
        return playground
    return None

def url_for(endpoint, **kwargs):
    if 'jsembed' in this_thread.misc:
        kwargs['_external'] = True
        if endpoint == 'index':
            kwargs['js_target'] = this_thread.misc['jsembed']
    if COOKIELESS_SESSIONS:
        if endpoint == 'index':
            endpoint = 'html_index'
        kwargs['_external'] = True
    return base_url_for(endpoint, **kwargs)

@hookimpl(specname="url_for")
def url_for_adapter(endpoint, kwargs):
    return url_for(endpoint, **kwargs)
