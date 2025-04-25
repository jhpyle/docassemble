import string
import random
from docassemble.base.util import interview_list, create_user, get_user_list, get_user_info, set_user_info, manage_privileges

__all__ = ['get_permissions']

r = random.SystemRandom()

other_user = 29
other_interview = 'docassemble.base:data/questions/examples/madlibs.yml'


def random_alphanumeric(length):
    return ''.join(r.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(length))


def random_lower_string(length):
    return ''.join(r.choice(string.ascii_lowercase) for i in range(length))


def get_permissions():
    results = {}
    try:
        result = interview_list(user_id='all', filename=other_interview)
        assert result is not None
        result = interview_list(user_id=other_user, filename=other_interview)
        assert result is not None
        results['access_sessions'] = True
    except BaseException as err:
        results['access_sessions'] = err.__class__.__name__ + ": " + str(err)
    try:
        result = interview_list(user_id=other_user, action='delete_all', filename=other_interview)
        assert result is not None
        result = interview_list(user_id='all', action='delete_all', filename=other_interview)
        assert result is not None
        results['edit_sessions'] = True
    except BaseException as err:
        results['edit_sessions'] = err.__class__.__name__ + ": " + str(err)
    try:
        get_user_info(user_id=other_user)
        user_list = []
        next_id = None
        while True:
            (items, next_id) = get_user_list(next_id=next_id)
            user_list.extend(items)
            if not next_id:
                break
        assert len(user_list) > 0
        results['access_user_info'] = True
    except BaseException as err:
        results['access_user_info'] = err.__class__.__name__ + ": " + str(err)
    try:
        create_user(random_lower_string(8) + '@docassemble.org', random_alphanumeric(8), privileges=['user', 'customer'], info={'first_name': 'John', 'last_name': 'Smith'})
        results['create_user'] = True
    except BaseException as err:
        results['create_user'] = err.__class__.__name__ + ": " + str(err)
    try:
        set_user_info(user_id=other_user, first_name='Foo', last_name='Bar')
        results['edit_user_info'] = True
    except BaseException as err:
        results['edit_user_info'] = err.__class__.__name__ + ": " + str(err)
    try:
        set_user_info(user_id=other_user, password=random_lower_string(8))
        results['edit_user_password'] = True
    except BaseException as err:
        results['edit_user_password'] = err.__class__.__name__ + ": " + str(err)
    try:
        set_user_info(user_id=other_user, active=False)
        set_user_info(user_id=other_user, active=True)
        results['edit_user_active_status'] = True
    except BaseException as err:
        results['edit_user_active_status'] = err.__class__.__name__ + ": " + str(err)
    try:
        set_user_info(user_id=other_user, privileges=['user', 'trainer', 'customer'])
        set_user_info(user_id=other_user, privileges=['user', 'trainer'])
        results['edit_user_privileges'] = True
    except BaseException as err:
        results['edit_user_privileges'] = err.__class__.__name__ + ": " + str(err)
    try:
        result = manage_privileges('list')
        assert result is not None
        result = manage_privileges('inspect', 'customer')
        assert result is not None
        results['access_privileges'] = True
    except BaseException as err:
        results['access_privileges'] = err.__class__.__name__ + ": " + str(err)
    test_privilege = random_lower_string(10)
    try:
        result = manage_privileges('add', test_privilege)
        assert result is not None
        result = manage_privileges('remove', test_privilege)
        assert result is not None
        results['edit_privileges'] = True
    except BaseException as err:
        results['edit_privileges'] = err.__class__.__name__ + ": " + str(err)
    return results
