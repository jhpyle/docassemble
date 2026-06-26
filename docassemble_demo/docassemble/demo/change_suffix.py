# do not pre-load
from docassemble.base.language.core import update_language_function

def my_name_suffix():
    return ['Jr', 'Sr', 'II', 'III', 'IV', 'Esq', 'PhD']

update_language_function('en', 'name_suffix', my_name_suffix)
