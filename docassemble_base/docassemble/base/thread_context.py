import copy
import contextvars
from contextlib import contextmanager
from typing import Any, Dict
from types import SimpleNamespace
from werkzeug.local import LocalProxy
import markdown
from .hooks import (
    get_default_language,
    get_default_dialect,
    get_default_voice,
    get_default_country,
    get_default_locale,
)

_current_user_dict: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "current_user_dict"
)
_old_user_dict: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "old_user_dict"
)
_current_globals: contextvars.ContextVar[SimpleNamespace] = contextvars.ContextVar(
    "current_globals"
)

class GenericObject:

    def __init__(self):
        self.user = None
        self.role = 'user'


def empty_globals() -> SimpleNamespace:
    global_obj = SimpleNamespace()
    global_obj.language = get_default_language()
    global_obj.dialect = get_default_dialect()
    global_obj.voice = get_default_voice()
    global_obj.country = get_default_country()
    global_obj.locale = get_default_locale()
    global_obj.current_info = {}
    global_obj.internal = {}
    global_obj.initialized = False
    global_obj.session_id = None
    global_obj.current_package = None
    global_obj.interview = None
    global_obj.interview_status = None
    global_obj.evaluation_context = None
    global_obj.gathering_mode = {}
    global_obj.global_vars = GenericObject()
    global_obj.current_variable = []
    global_obj.open_files = set()
    global_obj.markdown = markdown.Markdown(extensions=['smarty', 'markdown.extensions.sane_lists', 'markdown.extensions.tables', 'markdown.extensions.attr_list', 'markdown.extensions.md_in_html', 'footnotes'], output_format='html5')
    global_obj.saved_files = {}
    global_obj.message_log = []
    global_obj.misc = {}
    global_obj.probing = False
    global_obj.prevent_going_back = False
    global_obj.current_question = None
    global_obj.current_section = None
    return global_obj

def copy_of_globals(original: SimpleNamespace) -> SimpleNamespace:
    global_obj = SimpleNamespace()
    global_obj.language = original.language
    global_obj.dialect = original.dialect
    global_obj.voice = original.voice
    global_obj.country = original.country
    global_obj.locale = original.locale
    global_obj.current_info = copy.deepcopy(original.current_info)
    global_obj.internal = {}
    global_obj.initialized = original.initialized
    global_obj.session_id = original.session_id
    global_obj.current_package = original.current_package
    global_obj.interview = original.interview
    global_obj.interview_status = original.interview_status
    global_obj.evaluation_context = None
    global_obj.gathering_mode = {}
    global_obj.global_vars = GenericObject()
    global_obj.current_variable = original.current_variable
    global_obj.open_files = original.open_files
    global_obj.markdown = original.markdown
    global_obj.saved_files = {}
    global_obj.message_log = []
    global_obj.misc = copy.deepcopy({k: v for k, v in original.misc.items() if not (k.startswith('yaml_') or k in ('pending_error', 'docx_subdocs', 'docx_include_count', 'docx_template', 'dbcache'))})
    global_obj.probing = False
    global_obj.prevent_going_back = False
    global_obj.current_question = None
    global_obj.current_section = None
    return global_obj

# def backup_thread_variables():
#     reset_context()
#     for key in ('pending_error', 'docx_subdocs', 'dbcache'):
#         if key in this_thread.misc:
#             del this_thread.misc[key]
#     backup = {}
#     for key in ('interview', 'interview_status', 'open_files', 'current_question'):
#         if hasattr(this_thread, key):
#             backup[key] = getattr(this_thread, key)
#     for key in ['language', 'dialect', 'country', 'locale', 'current_info', 'internal', 'initialized', 'session_id', 'current_package', 'interview', 'interview_status', 'evaluation_context', 'gathering_mode', 'global_vars', 'current_variable', 'saved_files', 'message_log', 'misc', 'probing', 'prevent_going_back', 'current_question']:
#         if hasattr(this_thread, key):
#             backup[key] = getattr(this_thread, key)
#             if key == 'global_vars':
#                 this_thread.global_vars = GenericObject()
#             elif key == 'misc':
#                 for key in [item for item in this_thread.misc.keys() if item.startswith('yaml_')]:
#                     del this_thread.misc[key]
#                 setattr(this_thread, key, copy.deepcopy(this_thread.misc))
#             elif key == 'current_info':
#                 setattr(this_thread, key, copy.deepcopy(getattr(this_thread, key)))
#             elif key in ('internal', 'gathering_mode', 'saved_files'):
#                 setattr(this_thread, key, {})
#             elif key in ('current_variable', 'message_log'):
#                 setattr(this_thread, key, [])
#     return backup


@contextmanager
def user_dict_context(user_dict: Dict[str, Any]):
    token = _current_user_dict.set(user_dict)
    try:
        yield user_dict
    finally:
        _current_user_dict.reset(token)


def get_current_user_dict() -> Dict[str, Any] | None:
    return _current_user_dict.get(None)


@contextmanager
def old_user_dict_context(user_dict: Dict[str, Any]):
    token = _old_user_dict.set(user_dict)
    try:
        yield user_dict
    finally:
        _old_user_dict.reset(token)


def get_old_user_dict() -> Dict[str, Any] | None:
    return _old_user_dict.get(None)


@contextmanager
def global_context(context_vars: SimpleNamespace):
    token = _current_globals.set(context_vars)
    try:
        yield context_vars
    finally:
        _current_globals.reset(token)


def get_globals() -> SimpleNamespace:
    return _current_globals.get(None)


this_thread: SimpleNamespace = LocalProxy(lambda: _current_globals.get(None))
