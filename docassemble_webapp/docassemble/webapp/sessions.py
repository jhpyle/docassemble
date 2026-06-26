from contextlib import contextmanager
from flask import session
from docassemble.base.error import DAException

# _session_backup: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
#     "session_backup"
# )

@contextmanager
def session_context():
    # token = _session_backup.set(backup_session())
    backup = backup_session()
    try:
        yield
    finally:
        # restore_session(_session_backup.get())
        # _session_backup.reset(token)
        restore_session(backup)


def backup_session():
    backup = {}
    for key in ('i', 'uid', 'key_logged', 'tempuser', 'user_id', 'encrypted', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'taskwait', 'phone_number', 'otp_secret', 'validated_user', 'github_next', 'next', 'sessions', 'alt_session'):
        if key in session:
            backup[key] = session[key]
    return backup


def restore_session(backup):
    for key in ('i', 'uid', 'key_logged', 'tempuser', 'user_id', 'encrypted', 'google_id', 'google_email', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'taskwait', 'phone_number', 'otp_secret', 'validated_user', 'github_next', 'next', 'sessions', 'alt_session'):
        if key in backup:
            session[key] = backup[key]


def clear_session(i):
    if 'sessions' in session and i in session['sessions']:
        del session['sessions'][i]
    session.modified = True


def clear_specific_session(i, uid):
    if 'sessions' in session and i in session['sessions']:
        if session['sessions'][i]['uid'] == uid:
            del session['sessions'][i]
    session.modified = True


def guess_yaml_filename():
    yaml_filename = None
    if 'i' in session and 'uid' in session:  # TEMPORARY
        yaml_filename = session['i']
    if 'sessions' in session:
        for item in session['sessions']:
            yaml_filename = item
            break
    return yaml_filename


def delete_obsolete():
    for name in ('i', 'uid', 'key_logged', 'encrypted', 'chatstatus'):
        if name in session:
            del session[name]
    session.modified = True


def get_session(i):
    if 'sessions' not in session:
        session['sessions'] = {}
    if i in session['sessions']:
        return session['sessions'][i]
    if 'i' in session and 'uid' in session:  # TEMPORARY
        session['sessions'][session['i']] = {'uid': session['uid'], 'encrypted': session.get('encrypted', True), 'key_logged': session.get('key_logged', False), 'chatstatus': session.get('chatstatus', 'off')}
        if i == session['i']:
            delete_obsolete()
            return session['sessions'][i]
        delete_obsolete()
    return None


def get_uid_for_filename(i):
    if 'sessions' not in session:
        session['sessions'] = {}
    if i not in session['sessions']:
        return None
    return session['sessions'][i]['uid']


def update_session(i, uid=None, encrypted=None, key_logged=None, chatstatus=None):
    if 'sessions' not in session:
        session['sessions'] = {}
    if i not in session['sessions'] or uid is not None:
        if uid is None:
            raise DAException("update_session: cannot create new session without a uid")
        if encrypted is None:
            encrypted = True
        if key_logged is None:
            key_logged = False
        if chatstatus is None:
            chatstatus = 'off'
        session['sessions'][i] = {'uid': uid, 'encrypted': encrypted, 'key_logged': key_logged, 'chatstatus': chatstatus}
    else:
        if uid is not None:
            session['sessions'][i]['uid'] = uid
        if encrypted is not None:
            session['sessions'][i]['encrypted'] = encrypted
        if key_logged is not None:
            session['sessions'][i]['key_logged'] = key_logged
        if chatstatus is not None:
            session['sessions'][i]['chatstatus'] = chatstatus
    session.modified = True
    return session['sessions'][i]


def get_session_uids():
    if 'i' in session:  # TEMPORARY
        get_session(session['i'])
    if 'sessions' in session:
        return [item['uid'] for item in session['sessions'].values()]
    return []
