from .config import main_page_parts
from ..hooks.impl import hookimpl

@hookimpl
def get_main_page_parts():
    return main_page_parts
