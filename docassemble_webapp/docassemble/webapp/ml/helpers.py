import re

def fix_group_id(the_package, the_file, the_group_id):
    if the_package == '_global':
        group_id_to_use = the_group_id
    else:
        group_id_to_use = the_package
        if re.search(r'^data/', the_file):
            group_id_to_use += ':' + the_file
        else:
            group_id_to_use += ':data/sources/ml-' + the_file + '.json'
        group_id_to_use += ':' + the_group_id
    return group_id_to_use

def ml_prefix(the_package, the_file):
    the_prefix = the_package
    if re.search(r'^data/', the_file):
        the_prefix += ':' + the_file
    else:
        the_prefix += ':data/sources/ml-' + the_file + '.json'
    return the_prefix
