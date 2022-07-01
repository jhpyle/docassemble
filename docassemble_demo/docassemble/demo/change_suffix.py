# do not pre-load
import docassemble.base.functions

def my_name_suffix():
    return ['Jr', 'Sr', 'II', 'III', 'IV', 'Esq', 'PhD']

docassemble.base.functions.update_language_function('en', 'name_suffix', my_name_suffix)
