import time
import sys
import logging
import re
import os
from flask import request
from flask import has_request_context
from flask_login import current_user
from docassemble.base.logger import set_logmessage
from docassemble.base.thread_context import this_thread
from docassemble.webapp.config import (
    LOGSERVER,
    LOG_DIRECTORY,
    daconfig,
    in_celery,
    in_cron,
)
from docassemble.webapp.utils.request import get_requester_ip

sys_logger = None

def syslog_message(message):
    message = re.sub(r'\n', ' ', message)
    if has_request_context():
        try:
            if current_user and current_user.is_authenticated:
                the_user = current_user.email
            else:
                the_user = "anonymous"
            the_current_info = getattr(this_thread, 'current_info', {})
            sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': get_requester_ip(request), 'yamlfile': the_current_info.get('yaml_filename', 'na'), 'user': the_user, 'session': the_current_info.get('session', 'na')})
        except BaseException as err:
            sys.stderr.write("Error writing log message " + str(message) + "\n")
            try:
                sys.stderr.write("Error was " + err.__class__.__name__ + ": " + str(err) + "\n")
            except:
                pass
    else:
        try:
            sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': 'localhost', 'yamlfile': 'na', 'user': 'na', 'session': 'na'})
        except BaseException as err:
            sys.stderr.write("Error writing log message " + str(message) + "\n")
            try:
                sys.stderr.write("Error was " + err.__class__.__name__ + ": " + str(err) + "\n")
            except:
                pass


def syslog_message_with_timestamp(message):
    syslog_message(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message)

LOGFORMAT = daconfig.get('log format', 'docassemble: ip=%(clientip)s i=%(yamlfile)s uid=%(session)s user=%(user)s %(message)s')


class UnsilenceableLogger(logging.Logger):
    def isEnabledFor(self, level):
        return level >= self.level


def add_log_handler():
    tries = 0
    while tries < 5:
        try:
            docassemble_log_handler = logging.FileHandler(filename=os.path.join(LOG_DIRECTORY, 'docassemble.log'))
        except PermissionError:
            sys.stderr.write("Unable to open docassemble.log; trying again\n")
            time.sleep(1)
            tries += 1
            continue
        sys_logger.addHandler(docassemble_log_handler)
        if os.environ.get('SUPERVISORLOGLEVEL', 'info') == 'debug':
            stderr_log_handler = logging.StreamHandler(stream=sys.stderr)
            sys_logger.addHandler(stderr_log_handler)
        break

if not (in_celery or in_cron or daconfig.get('log to std', False)):
    logging.setLoggerClass(UnsilenceableLogger)
    sys_logger = logging.getLogger('docassemble')
    logging.setLoggerClass(logging.Logger)
    sys_logger.setLevel(logging.DEBUG)
    sys_logger.propagate = False
    add_log_handler()
    if LOGSERVER is None:
        set_logmessage(syslog_message_with_timestamp)
    else:
        set_logmessage(syslog_message)
