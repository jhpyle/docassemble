import copy
import datetime
from flask_login import current_user
from docassemble.webapp.interview.config import initial_dict

def fresh_dictionary():
    the_dict = copy.deepcopy(initial_dict)
    add_timestamps(the_dict)
    return the_dict


def add_timestamps(the_dict, manual_user_id=None):
    nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    the_dict['_internal']['starttime'] = nowtime
    the_dict['_internal']['modtime'] = nowtime
    if manual_user_id is not None or (current_user and current_user.is_authenticated):
        if manual_user_id is not None:
            the_user_id = manual_user_id
        else:
            the_user_id = current_user.id
        the_dict['_internal']['accesstime'][the_user_id] = nowtime
    else:
        the_dict['_internal']['accesstime'][-1] = nowtime
