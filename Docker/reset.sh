#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_DEFAULT_LOCAL="local3.8"
export DA_CONFIG_FILE="${DA_CONFIG:-${DA_ROOT}/config/config.yml}"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"

export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export HOME=/var/www

source /dev/stdin < <(python -m docassemble.base.read_config "$DA_CONFIG_FILE")

# if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
#     supervisorctl --serverurl http://localhost:9001 stop nginx || exit 1
# fi

echo "`date` starting docassemble.webapp.restart" >&2
python -m docassemble.webapp.restart
echo "`date` finished docassemble.webapp.restart" >&2

if [ "${PIPINDEXURL:-null}" != "null" ]; then
    pip config set global.index-url "${PIPINDEXURL}"
else
    pip config unset global.index-url &> /dev/null
fi

if [ "${PIPEXTRAINDEXURLS:-null}" != "null" ]; then
    pip config set global.extra-index-url "${PIPEXTRAINDEXURLS}"
else
    pip config unset global.extra-index-url &> /dev/null
fi

if [[ $CONTAINERROLE =~ .*:(all|celery):.* ]]; then
    echo "`date` stopping celery" >&2
    supervisorctl --serverurl http://localhost:9001 stop celery || exit 1
    echo "`date` stopping celerysingle" >&2
    supervisorctl --serverurl http://localhost:9001 stop celerysingle || exit 1
    if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]]; then
	echo "`date` stopping rabbitmq" >&2
	supervisorctl --serverurl http://localhost:9001 stop rabbitmq || exit 1
    fi
    sleep 1
    if [[ $CONTAINERROLE =~ .*:(all|rabbitmq):.* ]]; then
	echo "`date` starting rabbitmq" >&2
	supervisorctl --serverurl http://localhost:9001 start rabbitmq || exit 1
    fi
    sleep 1
    echo "`date` starting celery" >&2
    supervisorctl --serverurl http://localhost:9001 start celery || exit 1
    echo "`date` starting celerysingle" >&2
    supervisorctl --serverurl http://localhost:9001 start celerysingle || exit 1
    echo "`date` finished resetting background task system" >&2
fi

if [[ $CONTAINERROLE =~ .*:(all|web):.* ]]; then
    echo "`date` stopping websockets" >&2
    supervisorctl --serverurl http://localhost:9001 stop websockets || exit 1
    sleep 1
    echo "`date` starting websockets" >&2
    supervisorctl --serverurl http://localhost:9001 start websockets || exit 1
    echo "`date` finished resetting websockets" >&2
fi

# killall -9 /usr/lib/libreoffice/program/soffice.bin &> /dev/null
# if [ "${DAWEBSERVER:-nginx}" = "nginx" ]; then
#     supervisorctl --serverurl http://localhost:9001 start nginx || exit 1
# fi

echo "`date` finished reset process" >&2
exit 0
